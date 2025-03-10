import pytz
from datetime import datetime
from slack_sdk.errors import SlackApiError
from src.slack.slack_api import slack_app
from src.db.fetch_requests import update_slack_response
from src.routes.route_fetch_requests import api_call  # Your external API call
from config.config import SlackCred
from slack_sdk import WebClient

client = WebClient(token=SlackCred.slack_token)  # Slack Web client to update message


def get_user_email(user_id):
    try:
        response = client.users_info(user=user_id)
        return response['user']['profile']['email']
    except SlackApiError as e:
        print(f"Error fetching user info: {e.response['error']}")


@slack_app.action("approve_button")
def handle_approve_button(ack, body, client):
    ack()  # Acknowledge action
    user_id = body['user']['id']
    request_reference = int(body['actions'][0]['value'])
    channel_id = body['channel']['id']
    message_ts = body['message']['ts']
    
    email = get_user_email(user_id)
    api_call(email, "approved")  # External API call

    update_slack_response(request_reference, "approved", datetime.now(pytz.timezone('US/Eastern')))
    
    # Update Slack message
    client.chat_update(
        channel=channel_id,
        ts=message_ts,
        text="You have approved the request.",
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "You have approved the request."}
            }
        ]
    )
    print(f"User {email} approved the request.")


@slack_app.action("reject_button")
def handle_reject_button(ack, body, client):
    ack()  # Acknowledge action
    user_id = body['user']['id']
    request_reference = int(body['actions'][0]['value'])
    channel_id = body['channel']['id']
    message_ts = body['message']['ts']

    email = get_user_email(user_id)
    api_call(email, "rejected")  # External API call

    update_slack_response(request_reference, "rejected", datetime.now(pytz.timezone('US/Eastern')))

    # Update Slack message
    client.chat_update(
        channel=channel_id,
        ts=message_ts,
        text="You have rejected the request.",
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "You have rejected the request."}
            }
        ]
    )
    print(f"User {email} rejected the request.")
