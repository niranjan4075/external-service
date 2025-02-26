from fastapi import FastAPI, Form, Request
import json
import logging
from database.model import Device,Request,Inventory
from fastapi import FastAPI, Depends
from sqlalchemy.orm import aliased, Session
from sqlalchemy.sql import func, cast
from sqlalchemy import Integer,String,text
from database.model import get_db
from fastapi import FastAPI, WebSocket
from sqlalchemy.orm import Session
from database.model import SessionLocal
import asyncpg
from config import DbCred, DbCred
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio
from database.model import Base
from contextlib import asynccontextmanager
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from sqlalchemy.sql.expression import select
from datetime import datetime,timezone
from config import DbCred

Async_DATABASE_URL = DbCred.async_db_url
async_engine = create_async_engine(Async_DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    task = asyncio.create_task(listen_for_new_requests(await anext(get_async_db())))
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
app = FastAPI(lifespan=lifespan)

# Configure logging
logging.basicConfig(level=logging.INFO)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)
async def get_async_db():
    async with AsyncSessionLocal() as db:
        yield db

async def listen_for_new_requests(db: AsyncSession):
    last_request_time = datetime.now(timezone.utc)

    while True:
        await asyncio.sleep(5)

        try:
            new_requests = await db.execute(
                select(Request).where(Request.request_time_local > last_request_time)
            )

            new_requests_list = new_requests.scalars().all()

            if new_requests_list:
                for request in new_requests_list:
                    query = (
                select(
                    Request.first_name,
                    Request.last_name,
                    Request.recipient_email,
                    Request.requester_email,
                    Request.phone_number,
                    Device.device_name,
                    Device.device_type,
                    Device.device_id,
                    Inventory.user_associateid,
                    Inventory.device_type,
                    Inventory.device_model,
                    Inventory.device_name
                )
                .join(Device,
                      cast(func.regexp_replace(func.split_part(Request.device_quantities.cast(String), ':', 1),
                                               '[^0-9]', '', 'g'), Integer) == Device.device_id)
                .join(Inventory, Request.replaced_item_id == Inventory.item_id)
            )

            result = await db.execute(query)
            data = result.fetchall()
            for i in data:
                print("ssj",i)
                slack_obj.send_message(i)


                last_request_time = new_requests_list[-1].request_time_local

        except Exception as e:
            print(f"Error listening for new requests: {e}")

@app.post("/slack/interactive")
async def slack_interactive(payload: str = Form(...)):
    """Handle Slack interactive button responses."""
    try:
        data = json.loads(payload)  # Parse JSON payload
        user_response = data["actions"][0]["value"]  # "approve" or "deny"
        user_id = data["user"]["id"]  # User who clicked
        channel_id = data["channel"]["id"]  # Slack Channel ID

        logging.info(f"User {user_id} responded with {user_response} in channel {channel_id}")

        return {
            "text": f"Your response '{user_response}' has been recorded!"
        }
    except Exception as e:
        logging.error(f"Error processing Slack interaction: {str(e)}")
        return {"text": "An error occurred while processing your response."}
@app.post("/create_request/")
def create_request(first_name: str, last_name: str, recipient_email: str, requester_email: str, device_quantities: dict, address_id: int, db: Session = Depends(get_db)):
    db_request = Request(
        first_name=first_name,
        last_name=last_name,
        recipient_email=recipient_email,
        requester_email=requester_email,
        device_quantities=device_quantities,
        request_time_local=datetime.now(timezone.utc),
        address_id=address_id,
        action_email_status=0
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request
if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,port=8001)



if __name__=="__main__":
    import uvicorn
    uvicorn.run(app)
