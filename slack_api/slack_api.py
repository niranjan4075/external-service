import os
import logging
import requests
from config import SlackCred

class SlackMessage:
    def __init__(self):
        self.slack_token= SlackCred.slack_token
        self.url=f"{SlackCred.slack_url}/api/chat.postMessage"
        self.channel_name=SlackCred.channel_name

    def send_message(self,request,channel_name):
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
					"text": "*First Name:*\n sbdjb"
				},
				{
					"type": "mrkdwn",
					"text": "*Last Name:*\nsbdkjbk"
				},
				{
					"type": "mrkdwn",
					"text": "*Requester Email:*\ns"
				},
				{
					"type": "mrkdwn",
					"text": "*Recipient Email:*\nsn"
				},
				{
					"type": "mrkdwn",
					"text": "*Phone Number:*\n mn"
				},
				{
					"type": "mrkdwn",
					"text": "*Associate ID:*\nxnm"
				},
				{
					"type": "mrkdwn",
					"text": "*Device Type:*\n nb"
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
