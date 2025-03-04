class Templates:
	def get_manager_template(self,req):
		manager_temp=[
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
					{
						"type": "mrkdwn",
						"text": "*Requester:*\n "+ req["first_name"] +" " +req["last_name"]
					},

					{
						"type": "mrkdwn",
						"text": "*Requested Device:*\n" +req["device"]["device_name"]+"/"+ req["device"]["device_model"]
					},
					{
						"type": "mrkdwn",
						"text": "*Requested OS :*\n" +req["device"]["device_os"]
					},
					{
						"type": "mrkdwn",
						"text": "*Reason For Request:*\n"
					},
					{
						"type": "mrkdwn",
						"text": "*if the os  is sutiable for  the work enviornment ,approve the request.*"
					},
					{
						"type": "mrkdwn",
						"text": "*if the os is not suitable ,reject the request*"
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
						"action_id": "approve_button"
					},
					{
						"type": "button",
						"text": {
							"type": "plain_text",
							"emoji": True,
							"text": "Deny"
						},
						"style": "danger",
						"action_id": "reject_button"
					}
				]
			}
		]
		return manager_temp
	def channel_template(self,req):
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
		return channel_template
