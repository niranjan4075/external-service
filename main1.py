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
                    print(f"New request found: {request.request_reference}")
                    print(f"First Name: {request.first_name}")
                    print(f"Request Time: {request.request_time_local}")

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



if __name__=="__main__":
    import uvicorn
    uvicorn.run(app)
