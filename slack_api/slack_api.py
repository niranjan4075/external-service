import os
import logging
import requests
from config import SlackCred

class SlackMessage:
    def __init__(self):
        self.slack_token= SlackCred.slack_token
        self.url=f"{SlackCred.slack_url}/api/chat.postMessage"
        self.channel_name=SlackCred.channel_name

    def send_message(self,data):
        payload = {
            "channel": self.channel_name,  # Replace with your channel ID
            "text": "Please approve or reject the request:",  # Text fallback
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "You have a new request:\n*<fakeLink.toEmployeeProfile.com|Fred Enriquez - New device request>*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Type:*\nComputer (laptop)"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*When:*\nSubmitted Aut 10"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Last Update:*\nMar 10, 2015 (3 years, 5 months)"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Reason:*\nAll vowel keys aren't working."
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Specs:*\n\"Cheetah Pro 15\" - Fast, really fast\""
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
                            "value": "click_me_123"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "emoji": True,
                                "text": "Deny"
                            },
                            "style": "danger",
                            "value": "click_me_123"
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


