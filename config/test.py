import threading
import pytz
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from config import SlackCred
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_api.slack_api import app as slack_app
from message_templates.templates import Templates
import logging
from fastapi.middleware.cors import CORSMiddleware
from external_api.external_api import api_call
from database.database import start_polling_loop



logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

app = FastAPI(debug=True)
templates_obj = Templates()

origins=[
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_creddentials=True,
    allow_methods=["*"],
    allow_headers=["*"]

)

SLACK_APP_TOKEN = SlackCred.slack_app_token
client = WebClient(token=SlackCred.slack_token)



lock = threading.Lock()


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
    api_call(body["first_name"],body["last_name"])
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
