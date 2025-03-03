import time
import json
from sqlalchemy.orm import sessionmaker
from database.models import Request, Inventory, Device, engine


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_last_request_id():
    """Fetch the last request ID from the database on startup."""
    session = SessionLocal()
    try:
        last_request = session.query(Request).order_by(Request.request_reference.desc()).first()
        return last_request.request_reference if last_request else 0
    finally:
        session.close()


# Initialize last_checked_id with the highest existing request_reference
last_checked_id = get_last_request_id()


def fetch_new_requests():
    global last_checked_id
    session = SessionLocal()

    try:
        # Fetch new requests with a higher request_reference than last_checked_id
        new_requests = (
            session.query(
                Request.request_reference,
                Request.first_name,
                Request.last_name,
                Request.recipient_email,
                Request.requester_email,
                Request.phone_number,
                Inventory.user_associatedid,
                Inventory.device_type,
                Inventory.device_model,
                Inventory.device_name,
            )
            .join(Inventory, Request.replaced_item_id == Inventory.item_id)
            .filter(Request.request_reference > last_checked_id)
            .all()
        )

        request_list = []

        for request in new_requests:
            request_dict = {
                "request_reference": request.request_reference,
                "first_name": request.first_name,
                "last_name": request.last_name,
                "recipient_email": request.recipient_email,
                "requester_email": request.requester_email,
                "phone_number": request.phone_number,
                "inventory": {
                    "user_associatedid": request.user_associatedid,
                    "device_type": request.device_type,
                    "device_model": request.device_model,
                    "device_name": request.device_name,
                },
            }
            request_list.append(request_dict)

            # Update last_checked_id to the latest request_reference
            last_checked_id = max(last_checked_id, request.request_reference)

        # Print results in JSON format
        if request_list:
            for req in request_list:
                print(req)
                slack_obj.send_message(req,channel)
                ### get user by email
                ### lookup by email
                ###  get user id
                slack_obj.send_message(req,user_channel)


    finally:
        session.close()


# Polling loop (Run in a background task or separate thread)
while True:
    fetch_new_requests()
    time.sleep(5)  # Check every 5 seconds