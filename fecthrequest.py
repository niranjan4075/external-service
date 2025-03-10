from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Integer, String
from src.db.database import get_db
from src.db.models import Request, Device, ProcessedRequest
from datetime import datetime

router = APIRouter()

@router.get("/fetch-new-requests/", tags=["Requests"])
def fetch_new_requests(db: Session = Depends(get_db)):
    """
    API to fetch new device requests and store processed ones.
    """

    try:
        # Subquery to get already processed request references
        processed_subquery = db.query(ProcessedRequest.request_reference)

        # Main query to get requests that are NOT processed yet
        new_requests = (
            db.query(
                Request.request_reference,
                Request.first_name,
                Request.last_name,
                Request.recipient_email,
                Request.requester_email,
                Request.phone_number,
            )
            .filter(~Request.request_reference.in_(processed_subquery))
            .order_by(Request.request_reference.asc())
            .all()
        )

        output = []

        # If new requests found, process and save in ProcessedRequest
        if new_requests:
            for request in new_requests:
                req_data = {
                    "request_reference": request.request_reference,
                    "first_name": request.first_name,
                    "last_name": request.last_name,
                    "recipient_email": request.recipient_email,
                    "requester_email": request.requester_email,
                    "phone_number": request.phone_number
                }

                output.append(req_data)

                # Add to processed requests
                processed_entry = ProcessedRequest(
                    request_reference=request.request_reference,
                    processed_time=datetime.utcnow(),
                    status='completed'
                )
                db.add(processed_entry)

            # Commit after processing all
            db.commit()
        else:
            return {"message": "No new device requests found."}

        return {"new_requests": output}

    except Exception as e:
        print("Error fetching new requests:", e)
        return {"error": str(e)}



from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, String
from src.db.database import Base

class ProcessedRequest(Base):
    __tablename__ = "processed_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_reference = Column(Integer, ForeignKey("requests.request_reference"), nullable=False, unique=True)
    processed_time = Column(TIMESTAMP(timezone=True), nullable=False)
    status = Column(String, nullable=False)  # Example values: 'completed', 'failed'


CREATE TABLE processed_requests (
    id SERIAL PRIMARY KEY,
    request_reference INTEGER NOT NULL UNIQUE,
    processed_time TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR NOT NULL,
    CONSTRAINT fk_request_reference FOREIGN KEY (request_reference) REFERENCES requests(request_reference)
);
