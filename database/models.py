from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, JSON, TIMESTAMP, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from contextlib import contextmanager

from config import DbCred

engine = create_engine(DbCred.db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Address(Base):
    __tablename__ = 'addresses'

    address_id = Column(Integer, primary_key=True, autoincrement=True)
    address_label = Column(String(255), nullable=False)
    address_label_2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    address_type = Column(String(50), nullable=False)

    # Relationship with Request table (One Address can have many Requests)
    requests = relationship("Request", back_populates="address")


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

    # Foreign Key for Address table
    address_id = Column(Integer, ForeignKey("addresses.address_id"), nullable=False)

    action_email_status = Column(Integer, nullable=False)
    confirmation_email_status = Column(Integer, default=0, nullable=False)

    # Foreign Key for Inventory table (when a request replaces an item)
    replaced_item_id = Column(Integer, ForeignKey("inventory.item_id"), nullable=True)
    replaced_item_code = Column(String, nullable=True)

    # Relationships
    address = relationship("Address", back_populates="requests")  # One request belongs to one address
    replaced_item = relationship("Inventory", back_populates="requests")  # One request can reference an inventory item


class Device(Base):
    __tablename__ = "devices"

    device_id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String, index=True)
    device_model = Column(String)
    device_type = Column(String)
    device_os = Column(String)
    weight = Column("device_weight", String)
    battery = Column(String)
    cpu = Column(String)
    memory = Column(String)
    memory_type = Column(String)
    screen_size = Column(String)
    storage = Column(String)
    network = Column(String)
    wireless = Column(String)
    graphics = Column(String)
    power = Column(String)
    description = Column(String)
    device_image = Column(LargeBinary)


class Inventory(Base):
    __tablename__ = "inventory"

    item_id = Column(Integer, primary_key=True)  # Changed from String to Integer to match Request FK
    device_name = Column(String, index=True)
    device_serialnumber = Column(String)
    device_type = Column(String)
    device_model = Column(String)
    user_jobtitle = Column(String)
    user_email = Column(String)
    device_eoldate = Column(String)
    device_leaseend = Column(String)
    user_firstname = Column(String)
    user_lastname = Column(String)
    user_associatedid = Column(String)
    user_executive = Column(Boolean)
    user_shortdept = Column(String)
    device_shortmfg = Column(String)
    device_laptoptype = Column(String)
    user_branch = Column(String)
    user_branchoffice = Column(String)
    user_city = Column(String)
    user_state = Column(String)
    device_receiveddate = Column(String)
    device_age = Column(String)
    device_yearreceived = Column(String)
    device_yearrefresh = Column(String)

    # Relationship with Request (One inventory item can be replaced in multiple requests)
    requests = relationship("Request", back_populates="replaced_item")
