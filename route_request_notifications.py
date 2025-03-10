from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from src.db.database import get_db
from src.db.models import Request
from src.db.fetch_requests import insert_slack_response
from src.slack.slack_api import (
    send_channel_message_with_buttons,
    send_channel_message_without_buttons,
    look_up_by_email
)
from src.utils.slack_templates import (
    create_slack_message_with_buttons,
    create_slack_message_without_buttons
)

router = APIRouter()

# Constants for channels
PUBLIC_CHANNEL_ID = "C12345678"  # <-- Replace with your real channel ID
DEFAULT_MANAGER_CHANNEL = "C12345678"  # <-- Fallback channel if manager not found

@router.post("/fetch-and-notify-requests/", tags=["Request Notifications"])
def fetch_and_notify_requests(db: Session = Depends(get_db)):
    """
    Fetch new device requests that are not yet notified and send Slack notifications
    to manager and channel, and store tracking in slack_response.
    """

    try:
        # Step 1: Fetch new requests that are NOT already in slack_response (unprocessed)
        subquery = db.query(Request.request_reference).filter(
            ~Request.request_reference.in_(
                db.query(Request.request_reference)
                .join_from(Request, 'slack_response', isouter=True)
                .filter(Request.request_reference == Request.request_reference)
            )
        )

        new_requests = db.query(
            Request.request_reference,
            Request.first_name,
            Request.last_name,
            Request.recipient_email,
            Request.requester_email,
            Request.phone_number,
            Request.managers_email
        ).filter(Request.request_reference.in_(subquery)).order_by(Request.request_reference.asc()).all()

        if not new_requests:
            return {"message": "No new device requests found."}

        # Step 2: Process each new request
        for req in new_requests:
            request_reference = req.request_reference
            first_name = req.first_name
            last_name = req.last_name
            recipient_email = req.recipient_email
            requester_email = req.requester_email
            phone_number = req.phone_number
            manager_email = req.managers_email

            # Step 3: Prepare Slack message and block
            message_with_buttons, block_with_buttons = create_slack_message_with_buttons(
                first_name, last_name, recipient_email, requester_email, phone_number, request_reference
            )

            message_without_buttons, block_without_buttons = create_slack_message_without_buttons(
                first_name, last_name, recipient_email, requester_email, phone_number
            )

            # Step 4: Look up manager's Slack ID
            manager_user = look_up_by_email(manager_email)
            manager_channel_id = manager_user["id"] if manager_user else DEFAULT_MANAGER_CHANNEL

            # Step 5: Send message to manager with buttons
            send_channel_message_with_buttons(
                channel_id=manager_channel_id,
                message=message_with_buttons,
                block=block_with_buttons
            )

            # Step 6: Send message to public channel without buttons
            send_channel_message_without_buttons(
                channel_id=PUBLIC_CHANNEL_ID,
                message=message_without_buttons,
                block=block_without_buttons
            )

            # Step 7: Insert to slack_response as pending
            insert_slack_response(
                db=db,
                request_reference=request_reference,
                notification_sent_time=datetime.utcnow(),
                status="pending",
                managers_email=manager_email
            )

        return {"message": f"Slack notifications sent for {len(new_requests)} requests."}

    except Exception as e:
        print(f"Error in fetch-and-notify-requests: {str(e)}")
        return {"error": str(e)}
