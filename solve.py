Sure! Below is the **complete Python script** in a single file with a detailed explanation at the top.

---

## **🚀 Slack Notification Handling & Approval System**
### **How This Code Solves the Problem**
This FastAPI-based system fetches new requests, sends Slack notifications with action buttons (Approve/Reject), and tracks user responses **per request**. The key improvements ensure that:
1. **Each Slack notification includes the `request_reference` (unique ID) in the button payload.**
2. **When a user clicks Approve/Reject, the handler extracts the corresponding `request_reference`.**
3. **The database logs the action and updates the Slack message accordingly.**
4. **Prevents duplicate notifications and ensures each request is processed once.**

---

### **📜 Full Python Code**
```python
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

# Initialize FastAPI app and Slack components
app = FastAPI()
templates_obj = Templates()

SLACK_APP_TOKEN = SlackCred.slack_app_token
client = WebClient(token=SlackCred.slack_token)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

processed_requests = set()
lock = threading.Lock()

def insert_slack_response(notification_sent_time, status=None, user_clicked_time=None, managers_email="", request_reference=None):
    try:
        session = SessionLocal()
        new_slack_response = NewSlack(
            notification_sent_time=notification_sent_time,
            status=status,
            user_clicked_time=user_clicked_time,
            managers_email=managers_email,
            request_reference=request_reference  # Store request ID
        )
        session.add(new_slack_response)
        session.commit()
        print(f"New Slack response record for request {request_reference} inserted successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error inserting Slack response for request {request_reference}:", e)
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

        for request in new_requests:
            if request.request_reference in processed_requests:
                continue

            send_slack_notification(request)
            processed_requests.add(request.request_reference)
            last_checked_id = max(last_checked_id, request.request_reference)

    except Exception as e:
        print("Error fetching new requests:", e)
    finally:
        session.close()

def send_slack_notification(request):
    """ Sends a Slack notification with a request_reference in the button action payload. """
    client.chat_postMessage(
        channel=SlackCred.channel_name,
        text="A new request requires your approval:",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Request ID:* {request.request_reference}\nClick a button below:"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve"},
                        "style": "primary",
                        "value": str(request.request_reference),  # Pass request ID
                        "action_id": "approve_button"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Reject"},
                        "style": "danger",
                        "value": str(request.request_reference),  # Pass request ID
                        "action_id": "reject_button"
                    }
                ]
            }
        ]
    )

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
        return response['user']['profile']['email']
    except SlackApiError as e:
        print(f"Error fetching user info: {e.response['error']}")

@slack_app.action("approve_button")
def handle_approve_button(ack, body, client):
    ack()
    user_id = body['user']['id']
    request_reference = body['actions'][0]['value']
    email = get_user_email(user_id)
    button_clicked_time = datetime.now(pytz.timezone('US/Eastern')).strftime('%m-%d-%Y - %I:%M %p EST')

    client.chat_update(
        channel=body['channel']['id'],
        ts=body['message']['ts'],
        text=f"✅ Request *{request_reference}* has been approved.",
        blocks=[]
    )

    insert_slack_response(datetime.now(), "approved", button_clicked_time, email, request_reference)
    print(f"User {email} approved request {request_reference} at {button_clicked_time}")

@slack_app.action("reject_button")
def handle_reject_button(ack, body, client):
    ack()
    user_id = body['user']['id']
    request_reference = body['actions'][0]['value']
    email = get_user_email(user_id)
    button_clicked_time = datetime.now(pytz.timezone('US/Eastern')).strftime('%m-%d-%Y - %I:%M %p EST')

    client.chat_update(
        channel=body['channel']['id'],
        ts=body['message']['ts'],
        text=f"❌ Request *{request_reference}* has been rejected.",
        blocks=[]
    )

    insert_slack_response(datetime.now(), "rejected", button_clicked_time, email, request_reference)
    print(f"User {email} rejected request {request_reference} at {button_clicked_time}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
```

---

### **🛠 How It Works**
1. **Fetches new requests** from the database.
2. **Sends Slack notifications** with Approve/Reject buttons.
3. **Stores request ID in button payload**.
4. **Handles button clicks**, extracts request ID, and updates Slack.
5. **Logs approvals/rejections in the database**.

Now, **each approval/rejection is linked to the correct request**. 🎯  
Let me know if you need modifications! 🚀😊
