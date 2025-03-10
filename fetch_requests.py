from sqlalchemy.orm import Session
from sqlalchemy import update
from datetime import datetime
from src.db.models import NewSlack


def insert_slack_response(
    db: Session,  # Session injected via Depends
    request_reference: int,
    notification_sent_time: datetime,
    status: str = None,
    user_clicked_time: datetime = None,
    managers_email: str = ""
):
    """
    Inserts a Slack response record into the database.
    """
    try:
        new_slack_response = NewSlack(
            request_reference=request_reference,
            notification_sent_time=notification_sent_time,
            status=status,
            user_clicked_time=user_clicked_time,
            managers_email=managers_email
        )
        db.add(new_slack_response)
        db.commit()
        print("New Slack response record inserted successfully.")
    except Exception as e:
        db.rollback()
        print("Error inserting Slack response:", e)


def update_slack_response(
    db: Session,  # Session injected via Depends
    request_reference: int,
    new_status: str,
    user_clicked_time: datetime
):
    """
    Updates the status and user_clicked_time of a Slack response based on request_reference.
    """
    try:
        stmt = (
            update(NewSlack)
            .where(NewSlack.request_reference == request_reference)
            .values(status=new_status, user_clicked_time=user_clicked_time)
        )
        result = db.execute(stmt)
        db.commit()
        print(f"Updated {result.rowcount} record(s) with request_reference: {request_reference}")
    except Exception as e:
        db.rollback()
        print(f"Error updating Slack response: {e}")
