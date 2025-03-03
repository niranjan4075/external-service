class Templates:
    manager_temp=[
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

    channel_template=[
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

