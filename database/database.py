import time
from datetime import datetime
from slack_api.slack_api import send_channel_message_with_buttons, look_up_by_email
from database.models import Request, Inventory, Device, engine, NewSlack
from config import SlackCred
from sqlalchemy import func, cast, Integer, String
from sqlalchemy.orm import sessionmaker



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
processed_requests = set()

def insert_slack_response(notification_sent_time, status=None, user_clicked_time=None, managers_email=""):
    try:
        session = SessionLocal()
        new_slack_response = NewSlack(
            notification_sent_time=notification_sent_time,
            status=status,
            user_clicked_time=user_clicked_time,
            managers_email=managers_email
        )
        session.add(new_slack_response)
        session.commit()
        print("New Slack response record inserted successfully.")
    except Exception as e:
        session.rollback()
        print("Error inserting Slack response:", e)
    finally:
        session.close()

def get_last_request_id():
    session = SessionLocal()
    try:
        last_request = session.query(Request).order_by(Request.request_reference.desc()).first()
        return last_request.request_reference if last_request else 0
    finally:
        session.close()

last_checked_id = get_last_request_id()

def fetch_new_requests():
    global last_checked_id
    session = SessionLocal()
    try:
        device_quantities_part = func.split_part(func.cast(Request.device_quantities, String), ',', 1)
        device_id_extracted = func.regexp_replace(device_quantities_part, '[^0-9]', '', 'g')
        device_id_extracted = "1"

        new_requests = (
            session.query(
                Request.request_reference,
                Request.first_name,
                Request.last_name,
                Request.recipient_email,
                Request.requester_email,
                Request.managers_email,
                Request.phone_number,
                Device.device_name,
                Device.device_type,
                Device.device_id,
                Device.device_os,
                Device.device_model,
                Inventory.user_associatedid,
                Inventory.device_type.label('inventory_device_type'),
                Inventory.device_model,
                Inventory.device_name.label('inventory_device_name'),
            )
            .select_from(Request)
            .join(Device, cast(device_id_extracted, Integer) == Device.device_id)
            .join(Inventory, Request.replaced_item_id == Inventory.item_id)
            .filter(Request.request_reference > last_checked_id)
            .order_by(Request.request_reference.asc())
            .all()
        )

        request_list = []
        for request in new_requests:
            if request.request_reference not in processed_requests:
                request_dict = {
                    "request_reference": request.request_reference,
                    "first_name": request.first_name,
                    "last_name": request.last_name,
                    "recipient_email": request.recipient_email,
                    "phone_number": request.phone_number,
                    "managers_email": request.managers_email,
                    "device": {
                        "device_name": request.device_name,
                        "device_type": request.device_type,
                        "device_id": request.device_id,
                        "device_os": request.device_os,
                        "device_model": request.device_model,
                    },
                    "inventory": {
                        "user_associatedid": request.user_associatedid,
                        "device_type": request.inventory_device_type,
                        "device_model": request.device_model,
                        "device_name": request.inventory_device_name,
                    },
                }
                request_list.append(request_dict)
                processed_requests.add(request.request_reference)
                last_checked_id = max(last_checked_id, request.request_reference)

        if request_list:
            for req in request_list:
                print(req)
                manager_template = templates_obj.get_manager_template(req)
                channel_template = templates_obj.channel_template(req)

                send_channel_message_with_buttons(SlackCred.channel_name, "test msg", channel_template)

                manager_id = look_up_by_email(req["managers_email"])["id"]
                if manager_id:
                    insert_slack_response(datetime.now(), status="notification_send", managers_email=req["managers_email"])
                    send_channel_message_with_buttons(manager_id, "test msg2", manager_template)
    except Exception as e:
        print("Error fetching new requests:", e)
    finally:
        session.close()

def start_polling_loop():
    while True:
        fetch_new_requests()
        time.sleep(5)
