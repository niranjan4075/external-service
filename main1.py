from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base, Session, sessionmaker
from sqlalchemy.sql.expression import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import asyncio
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import psycopg2  # Import psycopg2 for PostgreSQL

# Database setup (PostgreSQL)
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/postgres"  # Replace with your PostgreSQL connection details
engine = create_engine(DATABASE_URL)
Async_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"  # Replace with your PostgreSQL connection details
async_engine = create_async_engine(Async_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)

Base = declarative_base()

class Request(Base):
    __tablename__ = "requests"

    request_reference = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)
    requester_email = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    device_quantities = Column(JSON, nullable=False)
    request_time_local = Column(TIMESTAMP(timezone=True), nullable=False)
    address_id = Column(Integer, ForeignKey("addresses.address_id"), nullable=False)
    action_email_status = Column(Integer, nullable=False)
    confirmation_email_status = Column(Integer, default=0, nullable=False)
    replaced_item_id = Column(Integer, ForeignKey("inventory.item_id"), nullable=True)
    replaced_item_code = Column(String, nullable=True)

class Address(Base):
    __tablename__ = "addresses"
    address_id = Column(Integer, primary_key=True, index=True)
    street = Column(String)

class Inventory(Base):
    __tablename__ = "inventory"
    item_id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String)

Base.metadata.create_all(bind=engine)

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
