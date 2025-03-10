import pytz
from datetime import datetime
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient
from src.slack.slack_api import slack_app  # Import the Slack Bolt App instance
from src.db.fetch_requests import update_slack_response
from config.config import SlackCred

# Initialize WebClient (used for chat updates)
client = WebClient(token=SlackCred.slack_token)


# Function to get user email by Slack user ID
def get_user_email(user_id: str) -> str:
    try:
        response = client.users_info(user=user_id)
        return response['user']['profile']['email']
    except SlackApiError as e:
        print(f"Error fetching user info: {e.response['error']}")
        return ""


# Handle approve button click
@slack_app.action("approve_button")
def handle_approve_button(ack, body, client):
    ack()  # Acknowledge action

    user_id = body['user']['id']
    request_reference = int(body['actions'][0]['value'])
    channel_id = body['channel']['id']
    message_ts = body['message']['ts']

    # Get user email
    email = get_user_email(user_id)

    # Update database status
    update_slack_response(
        request_reference=request_reference,
        new_status="approved",
        user_clicked_time=datetime.now(pytz.timezone('US/Eastern'))
    )

    # Update Slack message
    client.chat_update(
        channel=channel_id,
        ts=message_ts,
        text="You have approved the request.",
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*You have approved the request.*"}
            }
        ]
    )

    print(f"User {email} approved the request.")


# Handle reject button click
@slack_app.action("reject_button")
def handle_reject_button(ack, body, client):
    ack()  # Acknowledge action

    user_id = body['user']['id']
    request_reference = int(body['actions'][0]['value'])
    channel_id = body['channel']['id']
    message_ts = body['message']['ts']

    # Get user email
    email = get_user_email(user_id)

    # Update database status
    update_slack_response(
        request_reference=request_reference,
        new_status="rejected",
        user_clicked_time=datetime.now(pytz.timezone('US/Eastern'))
    )

    # Update Slack message
    client.chat_update(
        channel=channel_id,
        ts=message_ts,
        text="You have rejected the request.",
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "*You have rejected the request.*"}
            }
        ]
    )

    print(f"User {email} rejected the request.")
