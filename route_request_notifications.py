from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from src.db.database import get_db
from src.db.fetch_requests import insert_slack_response
from src.routes.route_fetch_requests import fetch_new_requests
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
PUBLIC_CHANNEL_ID = "C12345678"  # Replace this with your actual Slack channel ID
DEFAULT_MANAGER_CHANNEL = "C12345678"  # Fallback if manager email is not found on Slack


@router.post("/fetch-and-notify-requests/", tags=["Request Notifications"])
def fetch_and_notify_requests(db: Session = Depends(get_db)):
    """
    API to fetch new requests and notify both manager (with buttons) and channel (without buttons).
    """

    try:
        # Step 1: Fetch new unprocessed requests
        response = fetch_new_requests(db)
        new_requests = response.get("new_requests", [])

        if not new_requests:
            return {"message": "No new device requests found."}

        # Step 2: Iterate over new requests to process and notify
        for req in new_requests:
            request_reference = req["request_reference"]
            first_name = req["first_name"]
            last_name = req["last_name"]
            recipient_email = req["recipient_email"]
            requester_email = req["requester_email"]
            phone_number = req["phone_number"]
            manager_email = req["managers_email"]

            # Step 3: Prepare Slack messages and blocks
            message_with_buttons, block_with_buttons = create_slack_message_with_buttons(
                first_name, last_name, recipient_email, requester_email, phone_number, request_reference
            )

            message_without_buttons, block_without_buttons = create_slack_message_without_buttons(
                first_name, last_name, recipient_email, requester_email, phone_number
            )

            # Step 4: Look up manager's Slack user ID via email
            manager_user = look_up_by_email(manager_email)
            manager_channel_id = manager_user["id"] if manager_user else DEFAULT_MANAGER_CHANNEL

            # Step 5: Send notification to manager with buttons (Approve/Reject)
            send_channel_message_with_buttons(
                channel_id=manager_channel_id,
                message=message_with_buttons,
                block=block_with_buttons
            )

            # Step 6: Send notification to public channel (without buttons)
            send_channel_message_without_buttons(
                channel_id=PUBLIC_CHANNEL_ID,
                message=message_without_buttons,
                block=block_without_buttons
            )

            # Step 7: Insert into slack_response table for tracking
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
