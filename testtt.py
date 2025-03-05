import time
import json
import logging
import threading
import pytz
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks
from slack_api.slack_api import send_channel_message_with_buttons, look_up_by_email
from sqlalchemy.orm import sessionmaker
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from database.models import Request, Inventory, Device, engine, NewSlack
from config import SlackCred
from sqlalchemy import func, cast, Integer, String
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_api.slack_api import app as slack_app
from message_templates.templates import Templates

app = FastAPI()
templates_obj = Templates()

SLACK_APP_TOKEN = SlackCred.slack_app_token
client = WebClient(token=SlackCred.slack_token)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

processed_requests = set()
lock = threading.Lock()

def insert_slack_response(notification_sent_time, status=None, user_clicked_time=None, managers_email=""):
    try:
        session = SessionLocal()
        new_slack_response = NewSlack(
            notification_sent_time=notification_sent_time,
            status=status,
            user_clicked_time=user_clicked_time,
            managers_email=managers_email
        )
        session.add(new_slack_response)
        session.commit()
        print("New Slack response record inserted successfully.")
    except Exception as e:
        session.rollback()
        print("Error inserting Slack response:", e)
    finally:
        session.close()

def get_last_request_id():
    session = SessionLocal()
    try:
        last_request = session.query(Request).order_by(Request.request_reference.desc()).first()
        return last_request.request_reference if last_request else 0
    finally:
        session.close()

last_checked_id = get_last_request_id()

def fetch_new_requests():
    global last_checked_id
    session = SessionLocal()
    try:
        device_quantities_part = func.split_part(func.cast(Request.device_quantities, String), ',', 1)
        device_id_extracted = func.regexp_replace(device_quantities_part, '[^0-9]', '', 'g')
        device_id_extracted = "1"

        new_requests = (
            session.query(
                Request.request_reference,
                Request.first_name,
                Request.last_name,
                Request.recipient_email,
                Request.requester_email,
                Request.managers_email,
                Request.phone_number,
                Device.device_name,
                Device.device_type,
                Device.device_id,
                Device.device_os,
                Device.device_model,
                Inventory.user_associatedid,
                Inventory.device_type.label('inventory_device_type'),
                Inventory.device_model,
                Inventory.device_name.label('inventory_device_name'),
            )
            .select_from(Request)
            .join(Device, cast(device_id_extracted, Integer) == Device.device_id)
            .join(Inventory, Request.replaced_item_id == Inventory.item_id)
            .filter(Request.request_reference > last_checked_id)
            .order_by(Request.request_reference.asc())
            .all()
        )

        request_list = []
        for request in new_requests:
            if request.request_reference not in processed_requests:
                request_dict = {
                    "request_reference": request.request_reference,
                    "first_name": request.first_name,
                    "last_name": request.last_name,
                    "recipient_email": request.recipient_email,
                    "phone_number": request.phone_number,
                    "managers_email": request.managers_email,
                    "device": {
                        "device_name": request.device_name,
                        "device_type": request.device_type,
                        "device_id": request.device_id,
                        "device_os": request.device_os,
                        "device_model": request.device_model,
                    },
                    "inventory": {
                        "user_associatedid": request.user_associatedid,
                        "device_type": request.inventory_device_type,
                        "device_model": request.device_model,
                        "device_name": request.inventory_device_name,
                    },
                }
                request_list.append(request_dict)
                processed_requests.add(request.request_reference)
                last_checked_id = max(last_checked_id, request.request_reference)

        if request_list:
            for req in request_list:
                print(req)
                manager_template = templates_obj.get_manager_template(req)
                channel_template = templates_obj.channel_template(req)

                send_channel_message_with_buttons(SlackCred.channel_name, "test msg", channel_template)

                manager_id = look_up_by_email(req["managers_email"])["id"]
                if manager_id:
                    insert_slack_response(datetime.now(), status="notification_send", managers_email=req["managers_email"])
                    send_channel_message_with_buttons(manager_id, "test msg2", manager_template)
    except Exception as e:
        print("Error fetching new requests:", e)
    finally:
        session.close()

def start_polling_loop():
    while True:
        fetch_new_requests()
        time.sleep(5)

polling_thread = threading.Thread(target=start_polling_loop)
polling_thread.daemon = True
polling_thread.start()

@app.get("/")
def read_root():
    return {"message": "FastAPI is running"}

@app.on_event("startup")
async def startup_event():
    handler = SocketModeHandler(slack_app, SLACK_APP_TOKEN)
    handler.start()

def get_user_email(user_id):
    try:
        response = client.users_info(user=user_id)
        user_info = response['user']
        email = user_info['profile']['email']
        return email
    except SlackApiError as e:
        print(f"Error fetching user info: {e.response['error']}")

@slack_app.action("approve_button")
def handle_approve_button(ack, body, client):
    ack()
    print("body:", body)
    user_id = body['user']['id']
    original_message = body['message']['ts']
    channel_id = body['channel']['id']
    email = get_user_email(user_id)
    button_clicked_time = datetime.now(pytz.timezone('US/Eastern')).strftime('%m-%d-%Y - %I:%M %p EST')

    client.chat_update(
        channel=channel_id,
        ts=original_message,
        text="You have approved the request.",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You have approved the request."
                }
            }
        ]
    )

    print(f"User {email} approved the request.")
    print(f"Button clicked at: {button_clicked_time}")

@slack_app.action("reject_button")
def handle_reject_button(ack, body, client):
    ack()
    user_id = body['user']['id']
    original_message = body['message']['ts']
    channel_id = body['channel']['id']
    email = get_user_email(user_id)
    button_clicked_time = datetime.now(pytz.timezone('US/Eastern')).strftime('%m-%d-%Y - %I:%M %p EST')

    client.chat_update(
        channel=channel_id,
        ts=original_message,
        text="You have rejected the request.",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "You have rejected the request."
                }
            }
        ]
    )

    print(f"User {email} rejected the request.")
    print(f"Button clicked at: {button_clicked_time}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
