from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from src.db.database import get_db
from src.db.models import Request, Device
from src.db.fetch_requests import insert_slack_response
from src.utils.slack_templates import Templates
from src.slack.slack_api import send_channel_message_with_buttons
from config.config import SlackCred

router = APIRouter()


@router.post("/fetch-and-notify-requests/", tags=["Request Notifications"])
def fetch_and_notify_requests(db: Session = Depends(get_db)):
    """
    API endpoint to fetch unprocessed device requests and send Slack notifications.
    """

    # 1. First, fetch all new requests that are NOT present in slack_response table.
    processed_request_refs = db.query(Request.request_reference).join(
        "slack_response", isouter=True
    ).filter(
        Request.request_reference == None  # Request ref not yet processed
    ).all()

    if not processed_request_refs:
        return {"message": "No new device requests found."}

    # Flattening list of tuples
    processed_request_refs = [ref[0] for ref in processed_request_refs]

    # 2. Fetch complete details for each unprocessed request
    new_requests = (
        db.query(
            Request.request_reference,
            Request.first_name,
            Request.last_name,
            Request.recipient_email,
            Request.requester_email,
            Request.phone_number,
            Device.device_name,
            Device.device_model,
            Device.device_type,
            Device.device_id,
            Device.device_os
        )
        .join(
            Device,
            Device.device_id == Request.device_quantities[0].cast(Integer)  # Assuming first device quantity
        )
        .filter(Request.request_reference.in_(processed_request_refs))
        .all()
    )

    if not new_requests:
        return {"message": "No new device requests found."}

    # 3. Loop through requests and send Slack messages
    template_obj = Templates()

    for req in new_requests:
        req_data = {
            "request_reference": req.request_reference,
            "first_name": req.first_name,
            "last_name": req.last_name,
            "device": {
                "device_name": req.device_name,
                "device_model": req.device_model,
                "device_os": req.device_os
            }
        }

        # Get Slack message block using template
        slack_message_block = template_obj.get_manager_template(req_data)

        # Insert into slack_response table to mark this request as notified
        try:
            insert_slack_response(
                db=db,
                request_reference=req.request_reference,
                notification_sent_time=datetime.utcnow(),
                managers_email=req.requester_email  # Assuming requester_email as manager
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to insert Slack response: {str(e)}")

        # Send Slack message
        try:
            send_channel_message_with_buttons(
                channel_id=SlackCred.channel_name,
                message="New Device Request Notification",
                block=slack_message_block
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send Slack message: {str(e)}")

    return {"message": f"Slack notifications triggered for {len(new_requests)} requests."}
