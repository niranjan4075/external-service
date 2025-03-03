import time
import json
import logging
import threading
from slack_api.slack_api import send_channel_message_with_buttons, look_up_by_email
from message_templates import Templates
from sqlalchemy.orm import sessionmaker
from database.models import Request, Inventory, Device, engine
from config import SlackCred
from sqlalchemy import func, cast, Integer
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_api.slack_api import app




SLACK_APP_TOKEN =SlackCred.slack_app_token




SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
        # Fetch new requests with a higher request_reference than last_checked_id
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
                Inventory.user_associatedid,
                Inventory.device_type,
                Inventory.device_model,
                Inventory.device_name,
            )
            .join(
                Device,
                cast(
                    func.regexp_replace(
                        func.split_part(Request.device_quantities, ":", 1),
                        '[^0-9]',
                        '',
                        'g'
                    ),
                    Integer
                ) == Device.device_id
            )
            .join(Inventory, Request.replaced_item_id == Inventory.item_id)
            .filter(Request.request_reference > last_checked_id)
            .all()
        )

        request_list = []

        for request in new_requests:
            request_dict = {
                "request_reference": request.request_reference,
                "first_name": request.first_name,
                "last_name": request.last_name,
                "recipient_email": request.recipient_email,
                "requester_email": request.requester_email,
                "phone_number": request.phone_number,
                "managers_email": request.managers_email,
                "devices":{
                    "device_name":request.device_name,
                    "device_type": request.device_type,
                    "device_id":request.device_id
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

                # Send messages to the appropriate channels using templates
                send_message(SlackCred.channel_name, req["request_reference"],
                             Templates.channel_template)  # Replace 'ss' with actual data
                manager_id = look_up_by_email(req["managers_email"])  # Look up the manager's Slack ID by email
                if manager_id:
                    send_message(manager_id, req["request_reference"],
                                 Templates.manager_temp)  # Replace 'ss' with actual data
    except Exception as e:
        print(f"Error fetching new requests: {e}")
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






