from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token="xoxb-your-slack-bot-token")

client.chat_postMessage(
    channel=channel,
    text="Laptop upgrade notice",   # fallback text (for notifications / search)
    blocks=[
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"""
Hello <@{associate_name}>,

Friendly reminder — your current laptop has been identified as due for an upgrade.  
This commitment to enhancing our technology comes as part of our response to the feedback we gathered 
from the most recent Associate Opinion Survey, and we are excited to help elevate your tech experience.

*Your Current Laptop Serial Number:* {serial_number.upper() if serial_number else ""}

*Next Steps:*
1. Visit the Hardware Storefront at https://geckotech.geico.com/.
2. Select your current laptop and browse for your new replacement option.
3. Enter your shipping details.
4. Submit your order.
"""
            }
        },
        { "type": "divider" },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": """
*Important Notes:*
1. Please make your selection today, Friday, Sep. 5.
2. Once your new laptop has shipped, you will receive an email with tracking information.  
   _Note: It may take a few weeks after your selection for your new laptop to be shipped._
3. Upon receiving your new laptop, you will have two weeks from the delivery date to set it up and return your old laptop along with the charger.  
   _Note: You will be provided with a pre-paid shipping label and a shipping box to return your laptop and charger._

If you have any questions or concerns about your laptop upgrade, please reach out to the Asset Management team at hardware-storefront@geico.com.

For tech support, please contact the *Tech Solution Center* at <tel:+18669862211|+1-866-986-2211> or join <#C07MLNJ7GB1|#tech-solution-center>.

Thank you for your attention,  
*Asset Management*
"""
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Visit Hardware Storefront"
                    },
                    "url": "https://geckotech.geico.com/",
                    "style": "primary"
                }
            ]
        }
    ]
)
