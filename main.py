

from fastapi import FastAPI, Form, Request
import json
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.post("/slack/interactive")
async def slack_interactive(payload: str = Form(...)):
    """Handle Slack interactive button responses."""
    try:
        data = json.loads(payload)  # Parse JSON payload
        user_response = data["actions"][0]["value"]  # "approve" or "deny"
        user_id = data["user"]["id"]  # User who clicked
        channel_id = data["channel"]["id"]  # Slack Channel ID

        logging.info(f"User {user_id} responded with {user_response} in channel {channel_id}")

        return {
            "text": f"Your response '{user_response}' has been recorded!"
        }
    except Exception as e:
        logging.error(f"Error processing Slack interaction: {str(e)}")
        return {"text": "An error occurred while processing your response."}

