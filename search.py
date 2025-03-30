# FastAPI app to search records by any of the selected fields
from fastapi import FastAPI, Query
from typing import Optional
from datetime import datetime

app = FastAPI()

@app.get("/search")
def search(
    request_reference: Optional[str] = Query(None),
    first_name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    recipient_email: Optional[str] = Query(None),
    requester_email: Optional[str] = Query(None),
    phone_number: Optional[str] = Query(None),
    request_type: Optional[str] = Query(None),
    device_name: Optional[str] = Query(None),
    device_model: Optional[str] = Query(None),
    device_type: Optional[str] = Query(None),
    device_os: Optional[str] = Query(None),
    notification_sent_date: Optional[str] = Query(None),  # YYYY-MM-DD
    user_clicked_date: Optional[str] = Query(None),       # YYYY-MM-DD
    status: Optional[str] = Query(None),
    response_status: Optional[str] = Query(None),
    page: int = Query(1, gt=0),
    order_by: Optional[str] = Query("r.request_time_local"),
    order_dir: Optional[str] = Query("DESC")
):
    limit = 30
    offset = (page - 1) * limit

    filters = {
        "r.request_reference": request_reference,
        "r.first_name": first_name,
        "r.last_name": last_name,
        "r.recipient_email": recipient_email,
        "r.requester_email": requester_email,
        "r.phone_number": phone_number,
        "r.request_type": request_type,
        "d.device_name": device_name,
        "d.device_model": device_model,
        "d.device_type": device_type,
        "d.device_os": device_os,
        "s.status": status,
        "e.response": response_status
    }

    conditions = [f"{key} ILIKE '%{value}%'" for key, value in filters.items() if value]

    if notification_sent_date:
        conditions.append(f"DATE(s.notification_sent_time) = '{notification_sent_date}'")
    if user_clicked_date:
        conditions.append(f"DATE(s.user_clicked_time) = '{user_clicked_date}'")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    safe_order_by = order_by if order_by in [
        "r.request_reference", "r.first_name", "r.last_name", "r.request_time_local",
        "s.notification_sent_time", "s.user_clicked_time", "e.response"
    ] else "r.request_time_local"

    safe_order_dir = "DESC" if order_dir and order_dir.upper() == "DESC" else "ASC"

    query = f"""
    SELECT 
        r.request_reference,
        r.first_name,
        r.last_name,
        r.recipient_email,
        r.requester_email,
        r.phone_number,
        r.request_time_local,
        r.action_email_status,
        r.confirmation_email_status,
        r.replaced_item_id,
        r.replaced_item_code,
        r.managers_email,
        r.request_type,
        d.device_name,
        d.device_model,
        d.device_type,
        d.device_os,
        s.notification_sent_time,
        s.status,
        s.user_clicked_time,
        e.response AS response_status
    FROM requests r
    LEFT JOIN devices d ON r.device_id = d.device_id
    LEFT JOIN slack_response s ON r.request_reference = s.request_reference
    LEFT JOIN eventstore e ON r.request_reference = e.request_reference
    {where_clause}
    ORDER BY {safe_order_by} {safe_order_dir}
    LIMIT {limit} OFFSET {offset}
    """

    return {
        "page": page,
        "per_page": limit,
        "order_by": safe_order_by,
        "order_dir": safe_order_dir,
        "sql_query": query.strip()
    }
