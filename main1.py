import time
import json
import logging
import threading
from slack_api.slack_api import send_channel_message_with_buttons, look_up_by_email
from message_templates import Templates
from sqlalchemy.orm import sessionmaker
from database.models import Request, Inventory, Device, engine,NewSlack
from config import SlackCred
from sqlalchemy import func, cast, Integer,String
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_api.slack_api import app
from message_templates.templates import Templates
from datetime import datetime

templates_obj=Templates()




SLACK_APP_TOKEN =SlackCred.slack_app_token




SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def insert_slack_response(notification_sent_time, status=None, user_clicked_time=None, managers_email=""):
    try:
        # Create a new Slack response record

        session = SessionLocal()
        new_slack_response = NewSlack(
            notification_sent_time=notification_sent_time,
            status=status,
            user_clicked_time=user_clicked_time,
            managers_email=managers_email
        )

        # Add the new record to the session
        session.add(new_slack_response)

        # Commit the transaction to the database
        session.commit()
        print("New Slack response record inserted successfully.")
    except Exception as e:
        # In case of an error, roll back the transaction
        session.rollback()

def get_last_request_id():
    """Fetch the last request ID from the database on startup."""
    session = SessionLocal()
    try:
        last_request = session.query(Request).order_by(Request.request_reference.desc()).first()
        return last_request.request_reference if last_request else 0
    finally:
        session.close()


# Initialize last_checked_id with the highest existing request_reference
last_checked_id = get_last_request_id()



def fetch_new_requests():
    global last_checked_id
    session = SessionLocal()



    try:
        #device_id_extracted = func.jsonb_object_keys(Request.device_quantities)
        #
        device_quantities_part = func.split_part(func.cast(Request.device_quantities, String), ',', 1)

        device_id_extracted = func.regexp_replace(device_quantities_part, '[^0-9]', '', 'g')
        device_id_extracted = "1"
        # SQLAlchemy Query
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
            .join(
                Device,
                cast(device_id_extracted, Integer) == Device.device_id  # Ensure correct type comparison
            )
            .join(Inventory, Request.replaced_item_id == Inventory.item_id)
            .filter(Request.request_reference > last_checked_id)  # Filtering new requests based on the last checked ID
            .order_by(Request.request_reference.asc())  # You might want to order by request_reference for efficiency
            .all()
        )

        request_list = []
        print(new_requests)
        print(last_checked_id)

        for request in new_requests:
            request_dict = {
                "request_reference": request.request_reference,
                "first_name": request.first_name,
                "last_name": request.last_name,
                "recipient_email": request.recipient_email,
                "requester_email": request.requester_email,
                "phone_number": request.phone_number,
                "managers_email": request.managers_email,
                "device":{
                    "device_name":request.device_name,
                    "device_type": request.device_type,
                    "device_id":request.device_id,
                    "device_os":request.device_os,
                    "device_model":request.device_model
                },
                "inventory": {
                    "user_associatedid": request.user_associatedid,
                    "device_type": request.device_type,
                    "device_model": request.device_model,
                    "device_name": request.device_name,
                },
            }
            request_list.append(request_dict)

            # Update last_checked_id to the latest request_reference
            last_checked_id = max(last_checked_id, request.request_reference)

        # Print results in JSON format
        if request_list:
            for req in request_list:
                print(req)
                # Send messages to the appropriate channels using templates
                manager_template= templates_obj.get_manager_template(req)
                channel_template=templates_obj.channel_template(req)
                send_channel_message_with_buttons(SlackCred.channel_name, req["request_reference"],
                             channel_template)  # Replace 'ss' with actual data
                manager_id = look_up_by_email(req["managers_email"])["id"] # Look up the manager's Slack ID by email
                if manager_id:
                    insert_slack_response(datetime.now(),status="notification_send",managers_email=req["managers_email"])
                    send_channel_message_with_buttons(manager_id, req["request_reference"],
                                 manager_template)  # Replace 'ss' with actual data
    except Exception as e:
        print("error",e)
    finally:
        session.close()



# Function to start the polling loop in a separate thread
def start_polling_loop():
    while True:
        fetch_new_requests()
        time.sleep(5)  # Check every 5 seconds


# Create and start a new thread for the polling loop
polling_thread = threading.Thread(target=start_polling_loop)
polling_thread.daemon = True  # Make the thread a daemon so it exits when the main program exits
polling_thread.start()

# Main application can continue here

@app.action("approve_button")
def handle_approve_button(ack, body, client):
    """Handles the approve button click."""
    ack()
    user_id = body["user"]["id"]
    client.chat_postMessage(
        channel=user_id,
        text="You have approved the request."
    )
    print(f"User {user_id} approved the request.")

@app.action("reject_button")
def handle_reject_button(ack, body, client):
    """Handles the reject button click."""
    ack()
    user_id = body["user"]["id"]
    client.chat_postMessage(
        channel=user_id,
        text="You have rejected the request."
    )
    print(f"User {user_id} rejected the request.")

if __name__=="__main__":
    ## handler part
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()






