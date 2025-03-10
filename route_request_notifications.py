from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from src.db.database import get_db
from src.db.models import Request
from src.db.fetch_requests import insert_slack_response
from src.slack.slack_api import send_channel_message_without_buttons, send_channel_message_with_buttons

from src.utils.slack_templates import Templates

router = APIRouter()

templates = Templates()

@router.post("/fetch-and-notify-requests/", tags=["Request Notifications"])
def fetch_and_notify_requests(db: Session = Depends(get_db)):
    """
    Fetch new device requests, notify managers and channel, and store in slack_response table to prevent duplicate notifications.
    """

    try:
        # Fetch already processed request_references from slack_response
        processed_references = db.query(Request.request_reference).filter(
            Request.request_reference.in_(
                db.query(Request.request_reference)
            )
        )

        # Fetch only new/unprocessed requests
        new_requests = db.query(
            Request.request_reference,
            Request.first_name,
            Request.last_name,
            Request.recipient_email,
            Request.requester_email,
            Request.phone_number,
            Request.managers_email
        ).filter(
            ~Request.request_reference.in_(processed_references)
        ).order_by(Request.request_reference.asc()).all()

        if not new_requests:
            return {"message": "No new device requests to notify."}

        # Process each request
        for req in new_requests:
            # Prepare template for manager with buttons
            manager_template = templates.get_manager_template({
                "first_name": req.first_name,
                "last_name": req.last_name,
                "device": {
                    "device_name": "Laptop",  # if any static/default or dynamic value
                    "device_model": "ModelX",  # as needed
                    "device_os": "Windows"  # as needed
                },
                "request_reference": req.request_reference
            })

            # Send to manager (with buttons)
            send_channel_message_with_buttons(
                channel_id=req.managers_email,  # Assuming Slack email mapped to user or channel
                message="New Device Request for Approval",
                block=manager_template
            )

            # Prepare template for channel (without buttons)
            channel_template = templates.channel_template({
                "first_name": req.first_name,
                "last_name": req.last_name,
                "recipient_email": req.recipient_email,
                "requester_email": req.requester_email,
                "phone_number": req.phone_number,
                "device": {
                    "device_name": "Laptop",
                    "device_model": "ModelX",
                    "device_os": "Windows"
                }
            })

            # Send to public channel (without buttons)
            send_channel_message_without_buttons(
                channel_id="public_channel_id",  # Replace with actual channel ID
                message="New Device Request Notification",
                block=channel_template
            )

            # Insert entry into slack_response to mark as processed
            insert_slack_response(
                db=db,
                request_reference=req.request_reference,
                notification_sent_time=datetime.now(),
                status='sent',
                user_clicked_time=None,
                managers_email=req.managers_email
            )

        db.commit()  # Commit all at once

        return {"message": f"Slack notifications sent for {len(new_requests)} requests."}

    except Exception as e:
        print(f"Error processing device requests: {e}")
        return {"error": str(e)}
