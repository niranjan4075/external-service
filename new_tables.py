class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    user_email = Column(String, nullable=False)
    manager_email = Column(String, nullable=False)

    # Relationship with Request
    requests = relationship("Request", back_populates="user")

class Request(Base):
    __tablename__ = "requests"

    request_reference = Column(Integer, primary_key=True, index=True)
    user_ref_id = Column(Integer, ForeignKey("users.id"), nullable=True)
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
    user = relationship("Users", back_populates="requests")  # One request belongs to one user
    address = relationship("Address", back_populates="requests")  # One request belongs to one address
    replaced_item = relationship("Inventory", back_populates="requests")  # One request can reference an inventory item
