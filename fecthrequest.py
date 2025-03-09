# src/routes/route_fetch_requests.py

from fastapi import APIRouter, Depends
from sqlalchemy import func, cast, Integer, String
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.db.models import Request, Device, ProcessedRequest

router = APIRouter()


@router.get("/fetch-new-requests/", tags=["Requests"])
def fetch_new_requests(db: Session = Depends(get_db)):
    """
    API to fetch new device requests and store processed ones.
    """

    try:
        # Subquery to get already processed request references
        processed_subquery = db.query(ProcessedRequest.request_reference)

        # Main query using your working join and extracting device_id
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
                Device.device_id
            )
            .join(
                Device,
                cast(
                    func.regexp_replace(
                        func.split_part(cast(Request.device_quantities, String), ':', 1),
                        '[^0-9]',
                        '',
                        'g'
                    ),
                    Integer
                ) == Device.device_id
            )
            .filter(~Request.request_reference.in_(processed_subquery))  # ✅ Exclude already processed
            .order_by(Request.request_reference.asc())
            .all()
        )

        output = []

        if new_requests:
            for request in new_requests:
                req_data = {
                    "request_reference": request.request_reference,
                    "first_name": request.first_name,
                    "last_name": request.last_name,
                    "recipient_email": request.recipient_email,
                    "requester_email": request.requester_email,
                    "phone_number": request.phone_number,
                    "device_name": request.device_name,
                    "device_model": request.device_model,
                    "device_type": request.device_type,
                    "device_id": request.device_id,
                }
                output.append(req_data)

                # ✅ Add to processed_requests table
                processed_entry = ProcessedRequest(request_reference=request.request_reference)
                db.add(processed_entry)

            db.commit()  # ✅ Save all processed entries

        else:
            return {"message": "No new device requests found."}

        return {"new_requests": output}

    except Exception as e:
        print("Error fetching new requests:", e)
        return {"error": str(e)}


class ProcessedRequest(Base):
    __tablename__ = "processed_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_reference = Column(Integer, ForeignKey("requests.request_reference"), nullable=False, unique=True)
    processed_time = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
