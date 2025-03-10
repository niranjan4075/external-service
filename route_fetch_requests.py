from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from src.db.database import get_db
from src.db.fetch_requests import insert_slack_response
from src.utils.slack_templates import Templates
from src.slack.slack_api import send_channel_message_with_buttons
from config.config import SlackCred

router = APIRouter()


@router.post("/trigger-slack-notification/")
def trigger_slack_notification(request_reference: int, db: Session = Depends(get_db)):
    """
    API endpoint to trigger Slack notification for a new device request.
    """

    # Simulate fetching device request details from DB
    # In real case, fetch actual data using request_reference
    req = {
        "request_reference": request_reference,
        "first_name": "John",
        "last_name": "Doe",
        "device": {
            "device_name": "Laptop",
            "device_model": "Dell XPS",
            "device_os": "Windows 11"
        }
    }

    # Generate Slack message block using Templates class
    template_obj = Templates()
    slack_message_block = template_obj.get_manager_template(req)

    # Insert into slack_response table
    try:
        insert_slack_response(
            db=db,
            request_reference=request_reference,
            notification_sent_time=datetime.utcnow(),
            managers_email="manager@example.com"  # Hardcoded now, can be dynamic
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert Slack response: {str(e)}")

    # Send message to Slack channel
    try:
        send_channel_message_with_buttons(
            channel_id=SlackCred.channel_name,
            message="New Device Request Notification",
            block=slack_message_block
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send Slack message: {str(e)}")

    return {"message": "Slack notification triggered successfully."}
