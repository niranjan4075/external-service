from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from src.db.database import get_db
from src.db.models import Request, ProcessedRequest
from src.db.fetch_requests import insert_slack_response
from src.slack.slack_api import send_direct_message_with_buttons, send_channel_message_without_buttons, look_up_by_email
from src.utils.slack_templates import Templates

router = APIRouter()

@router.post("/fetch-and-notify-requests/", tags=["Request Notifications"])
def fetch_and_notify_requests(db: Session = Depends(get_db)):
    """
    Fetch new device requests, notify managers via DM, and public channel.
    """

    try:
        # 1. Get already processed request references
        processed_references = db.query(ProcessedRequest.request_reference)

        # 2. Get unprocessed requests
        new_requests = (
            db.query(
                Request.request_reference,
                Request.first_name,
                Request.last_name,
                Request.recipient_email,
                Request.requester_email,
                Request.phone_number,
                Request.managers_email
            )
            .filter(~Request.request_reference.in_(processed_references))
            .order_by(Request.request_reference.asc())
            .all()
        )

        # 3. Initialize templates
        template = Templates()
        output = []

        if new_requests:
            for req in new_requests:
                # 4. Prepare message blocks
                manager_block = template.get_manager_template(req)
                public_block = template.get_public_template(req)

                # 5. Lookup manager Slack User ID using email
                manager_email = req.managers_email
                manager_user = look_up_by_email(manager_email)
                manager_user_id = manager_user["id"] if manager_user else None

                if manager_user_id:
                    # 6. Send Slack Direct Message with buttons to manager
                    send_direct_message_with_buttons(manager_user_id, "New Device Request", manager_block)
                else:
                    print(f"Manager Slack user not found for email: {manager_email}")

                # 7. Send Public Channel message without buttons
                send_channel_message_without_buttons("PUBLIC_CHANNEL_ID", "New Device Request (Public)", public_block)

                # 8. Insert into slack_response for tracking
                insert_slack_response(
                    db=db,
                    request_reference=req.request_reference,
                    notification_sent_time=datetime.now(),
                    status="sent",
                    managers_email=manager_email
                )

                # 9. Add to processed_request
                processed_entry = ProcessedRequest(
                    request_reference=req.request_reference,
                    processed_time=datetime.utcnow(),
                    status='completed'
                )
                db.add(processed_entry)

                # Output info
                output.append({
                    "request_reference": req.request_reference,
                    "manager_notified": manager_email
                })

            # 10. Commit all at once
            db.commit()
            return {"message": f"Slack notifications sent for {len(new_requests)} requests.", "details": output}

        else:
            return {"message": "No new device requests found."}

    except Exception as e:
        db.rollback()
        print(f"Error processing notifications: {e}")
        return {"error": str(e)}
