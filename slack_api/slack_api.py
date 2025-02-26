import os
import logging
import requests
from config import SlackCred

class SlackMessage:
    def __init__(self):
        self.slack_token= SlackCred.slack_token
        self.url=f"{SlackCred.slack_url}/api/chat.postMessage"
        self.channel_name=SlackCred.channel_name

    def send_message(self,request):
        payload = {
    "channel": self.channel_name,  # Replace with your channel ID
    "text": "Please approve or reject the request:",  # Text fallback
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*New Device Request*"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*First Name:*\n{request['first_name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Last Name:*\n{request['last_name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Requester Email:*\n{request['requester_email']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Recipient Email:*\n{request['recipient_email']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Phone Number:*\n{request['phone_number']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Associate ID:*\n{request['inventory']['user_associatedid']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Device Type:*\n{request['inventory']['device_type']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Device Name:*\n{request['inventory']['device_name']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Device Model:*\n{request['inventory']['device_model']}"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Device Serial Number:*\n[User fills in Device Serial Number]"
                },
                {
                    "type": "mrkdwn",
                    "text": "*Device EOL Date:*\n[User fills in Device EOL Date]"
                }
            ]
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Approve"
                    },
                    "style": "primary",
                    "value": "approve_device_request"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "emoji": True,
                        "text": "Deny"
                    },
                    "style": "danger",
                    "value": "deny_device_request"
                }
            ]
        }
    ]
}

        # Set the headers including the Authorization with the Bearer Token
        headers = {
            "Authorization": f"Bearer {self.slack_token}",
            "Content-Type": "application/json"
        }

        # Make the POST request to send the message
        response = requests.post(self.url, headers=headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                logging.info("Message sent successfully")
            else:
                logging.error(f"Error sending message: {data.get('error')}")
        else:
            logging.error(f"Failed to send message. HTTP status code: {response.status_code}")


