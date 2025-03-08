def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Route to fetch all requests
@app.get("/requests")
def get_requests(db: Session = Depends(get_db)):
    requests = db.query(Request).all()
    return requests
