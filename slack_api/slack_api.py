import os
import logging

from config import SlackCred
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize WebClient with your bot token
slack_token = SlackCred.slack_token
app = App(token=slack_token)


# Function to send a message using the WebClient
def send_channel_message_with_buttons(channel_id, message,block):
    """Sends a message to a channel with Approve and Reject buttons."""
    try:
        response = app.client.chat_postMessage(
            channel=channel_id,
            text=message,
            blocks=block
        )
        print(f"Sent message to channel {channel_id}: {response['ts']}")
    except SlackApiError as e:
        print(f"Error sending message to channel {channel_id}: {e.response['error']}")



def look_up_by_email(email):
    response = app.client.users_lookupByEmail(email=email)
    return response['user']

