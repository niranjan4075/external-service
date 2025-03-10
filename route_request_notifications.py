from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from src.db.database import get_db
from src.db.models import Request, ProcessedRequest
from src.db.fetch_requests import insert_slack_response
from src.utils.slack_templates import Templates
from src.slack.slack_api import send_channel_message_with_buttons
from config.config import SlackCred

router = APIRouter()


@router.post("/fetch-and-notify-requests/", tags=["Request Notifications"])
def fetch_and_notify_requests(db: Session = Depends(get_db)):
    """
    API to fetch new device requests not processed yet and trigger Slack notifications.
    """

    try:
        # 1. Subquery for processed request references
        processed_subquery = db.query(ProcessedRequest.request_reference)

        # 2. Main query to get unprocessed requests
        new_requests = (
            db.query(
                Request.request_reference,
                Request.first_name,
                Request.last_name,
                Request.recipient_email,
                Request.requester_email,
                Request.phone_number
            )
            .filter(~Request.request_reference.in_(processed_subquery))
            .order_by(Request.request_reference.asc())
            .all()
        )

        if not new_requests:
            return {"message": "No new device requests found."}

        # 3. Initialize Slack Templates object
        template_obj = Templates()

        # 4. Loop through and process each new request
        for req in new_requests:
            req_data = {
                "request_reference": req.request_reference,
                "first_name": req.first_name,
                "last_name": req.last_name,
                "device": {
                    "device_name": "Unknown",  # Placeholder if no device details
                    "device_model": "Unknown",
                    "device_os": "Unknown"
                }
            }

            # Generate Slack message block
            slack_message_block = template_obj.get_manager_template(req_data)

            # Insert into ProcessedRequest to mark as processed
            insert_slack_response(
                db=db,
                request_reference=req.request_reference,
                notification_sent_time=datetime.utcnow(),
                status="pending",
                managers_email=req.requester_email
            )

            # Send Slack notification
            send_channel_message_with_buttons(
                channel_id=SlackCred.channel_name,
                message="New Device Request Notification",
                block=slack_message_block
            )

        return {"message": f"Slack notifications sent for {len(new_requests)} requests."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")
