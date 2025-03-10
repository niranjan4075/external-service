import os
import logging
from config.config import SlackCred
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize WebClient & Bolt App with bot token
slack_token = SlackCred.slack_token
slack_app_token = SlackCred.slack_app_token

app = App(token=slack_token)


# Function to send Slack message with buttons (using WebClient via Bolt)
def send_channel_message_with_buttons(channel_id, message, block):
    """
    Sends a message to a Slack channel with Approve/Reject buttons.
    """
    try:
        response = app.client.chat_postMessage(
            channel=channel_id,
            text=message,  # Plain fallback text
            blocks=block   # Rich message with buttons
        )
        print(f"Sent message to channel {channel_id}: {response['ts']}")
    except SlackApiError as e:
        print(f"Error sending message to channel {channel_id}: {e.response['error']}")


# Function to look up user ID by email
def look_up_by_email(email):
    """
    Find Slack user by email address.
    """
    response = app.client.users_lookupByEmail(email=email)
    return response['user']


# Function to start Socket Mode (if needed for interactive components)
def start_socket_mode():
    """
    Starts Slack Socket Mode for interactive messages.
    """
    handler = SocketModeHandler(app, slack_app_token)
    handler.start()
