# src/db/fetch_requests.py

import time
from sqlalchemy import func, cast, Integer, String
from src.db.database import Session
from src.db.models import Device, Request

# Track processed requests and last checked ID globally
processed_requests = set()
last_checked_id = 0  # You can persist this in DB or file if needed


def fetch_new_requests():
    """
    Fetches new device requests and prints them if found.
    """
    global last_checked_id
    session = Session()
    try:
        # Extract device_id from device_quantities (first number in the string, like SQL query)
        device_quantities_part = func.split_part(
            func.cast(Request.device_quantities, String), ',', 1
        )
        device_id_extracted = func.regexp_replace(
            device_quantities_part, '[^0-9]', '', 'g'
        )

        # Fetch new requests joined with Device
        new_requests = (
            session.query(
                Request.request_reference,
                Request.first_name,
                Request.last_name,
                Request.recipient_email,
                Request.requester_email,
                Request.phone_number,
                Device.device_name,
                Device.device_model,
                Device.device_type,
                Device.device_id
            )
            .join(Device, cast(device_id_extracted, Integer) == Device.device_id)
            .filter(Request.request_reference > last_checked_id)
            .order_by(Request.request_reference.asc())
            .all()
        )

        # Print newly fetched requests
        if new_requests:
            print("\n==== New Device Requests Found ====")
            for request in new_requests:
                if request.request_reference not in processed_requests:
                    print(f"Request ID      : {request.request_reference}")
                    print(f"Name            : {request.first_name} {request.last_name}")
                    print(f"Recipient Email : {request.recipient_email}")
                    print(f"Requester Email : {request.requester_email}")
                    print(f"Phone Number    : {request.phone_number}")
                    print(f"Device Name     : {request.device_name}")
                    print(f"Device Model    : {request.device_model}")
                    print(f"Device Type     : {request.device_type}")
                    print(f"Device ID       : {request.device_id}")
                    print("=" * 40)

                    # Add to processed and update last_checked_id
                    processed_requests.add(request.request_reference)
                    last_checked_id = max(last_checked_id, request.request_reference)
        else:
            print("No new device requests found.")

    except Exception as e:
        print("Error fetching new requests:", e)
    finally:
        session.close()


def start_polling(interval_seconds=5):
    """
    Starts an infinite polling loop to fetch new device requests periodically.
    :param interval_seconds: Interval time in seconds between each polling.
    """
    print(f"Starting polling for new device requests every {interval_seconds} seconds...")
    while True:
        fetch_new_requests()
        time.sleep(interval_seconds)
