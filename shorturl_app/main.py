from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, TodoItem
from schemas import TodoCreate, TodoResponse
from typing import List

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ToDo Service")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/items", response_model=TodoResponse)
def create_item(item: TodoCreate, db: Session = Depends(get_db)):
    db_item = TodoItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items", response_model=List[TodoResponse])
def get_items(db: Session = Depends(get_db)):
    return db.query(TodoItem).all()

@app.get("/items/{item_id}", response_model=TodoResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(TodoItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.put("/items/{item_id}", response_model=TodoResponse)
def update_item(item_id: int, data: TodoCreate, db: Session = Depends(get_db)):
    item = db.query(TodoItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for k, v in data.dict().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(TodoItem).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted"}
