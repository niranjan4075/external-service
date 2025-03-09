# src/db/fetch_requests.py

import time
import threading
from sqlalchemy import func, cast, Integer, String
from src.db.database import Session
from src.db.models import Device, Request


# Track processed requests and last checked ID globally
processed_requests = set()
last_checked_id = 0  # You can persist this if needed


def fetch_new_requests():
    """
    Fetch new device requests and print them if found.
    """
    global last_checked_id
    session = Session()
    try:
        device_quantities_part = func.split_part(func.cast(Request.device_quantities, String), ',', 1)
        device_id_extracted = func.regexp_replace(device_quantities_part, '[^0-9]', '', 'g')

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
    :param interval_seconds: Time between each polling iteration.
    """
    def poll():
        while True:
            fetch_new_requests()
            time.sleep(interval_seconds)

    # Run polling in background thread so FastAPI main thread is free
    polling_thread = threading.Thread(target=poll, daemon=True)
    polling_thread.start()


from fastapi import FastAPI
from src.routes.route_search import router
from src.db.database import engine, models
from src.db.fetch_requests import start_polling  # Import polling function

app = FastAPI(debug=True)

# Register routers
app.include_router(router, prefix="/search", tags=["Search"])

# DB tables creation
models.Base.metadata.create_all(bind=engine)

# Start polling on startup
@app.on_event("startup")
async def startup_event():
    start_polling(5)  # Poll every 5 seconds, adjustable interval

# Uvicorn run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main1:app", host="0.0.0.0", port=8008, reload=True)

uvicorn main1:app --reload --host 0.0.0.0 --port 8008

