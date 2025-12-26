from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import string, random

from database import SessionLocal, engine
from models import Base, ShortURL
from schemas import ShortenRequest, ShortenResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Short URL Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_short_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(data: ShortenRequest, db: Session = Depends(get_db)):
    short_id = generate_short_id()
    db_obj = ShortURL(short_id=short_id, full_url=data.url)
    db.add(db_obj)
    db.commit()
    return {"short_url": f"/{short_id}"}

@app.get("/{short_id}")
def redirect(short_id: str, db: Session = Depends(get_db)):
    link = db.query(ShortURL).filter_by(short_id=short_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    return RedirectResponse(link.full_url)

@app.get("/stats/{short_id}")
def stats(short_id: str, db: Session = Depends(get_db)):
    link = db.query(ShortURL).filter_by(short_id=short_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Not found")
    return {"short_id": link.short_id, "full_url": link.full_url}
