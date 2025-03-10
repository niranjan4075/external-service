class Templates:

    def get_manager_template(self, req):
        """
        Slack template with Approve/Reject buttons for managers.
        """
        manager_temp = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*New Device Request Notification*"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "*Requester:*\n" + req["first_name"] + " " + req["last_name"]},
                    {"type": "mrkdwn", "text": "*Requested Device:*\n" + req["device"]["device_name"] + "/" + req["device"]["device_model"]},
                    {"type": "mrkdwn", "text": "*Requested OS :*\n" + req["device"]["device_os"]},
                    {"type": "mrkdwn", "text": "*Reason For Request:*\n"},
                    {"type": "mrkdwn", "text": "_If the OS is suitable for the work environment, approve the request._"},
                    {"type": "mrkdwn", "text": "_If the OS is not suitable, reject the request._"}
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
                        "action_id": "approve_button",
                        "value": str(req["request_reference"])
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "Reject"
                        },
                        "style": "danger",
                        "action_id": "reject_button",
                        "value": str(req["request_reference"])
                    }
                ]
            }
        ]
        return manager_temp

    def channel_template(self, req):
        """
        Slack channel notification template without buttons.
        """
        channel_template = [
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
                    {"type": "mrkdwn", "text": "*First Name:*\n" + req["first_name"]},
                    {"type": "mrkdwn", "text": "*Last Name:*\n" + req["last_name"]},
                    {"type": "mrkdwn", "text": "*Requester Email:*\n" + req["requester_email"]},
                    {"type": "mrkdwn", "text": "*Recipient Email:*\n" + req["recipient_email"]},
                    {"type": "mrkdwn", "text": "*Phone Number:*\n" + req["phone_number"]},
                    {"type": "mrkdwn", "text": "*Associate ID:*\n" + req["associate_id"]},
                    {"type": "mrkdwn", "text": "*Device Type:*\n" + req["device_type"]},
                    {"type": "mrkdwn", "text": "*Device Serial Number:*\n[User fills in Device Serial Number]"},
                    {"type": "mrkdwn", "text": "*Device EOL Date:*\n[User fills in Device EOL Date]"}
                ]
            }
        ]
        return channel_template
