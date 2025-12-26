from fastapi import FastAPI, HTTPException
import sqlite3
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="ToDo Service")

# Путь к базе данных в Docker volume
DB_PATH = Path("data/todo.db")

# -----------------------
# Модели Pydantic
# -----------------------
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: Optional[bool] = False

class TodoResponse(TodoCreate):
    id: int

# -----------------------
# Инициализация базы
# -----------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

# -----------------------
# CRUD эндпоинты
# -----------------------

# CREATE
@app.post("/items", response_model=TodoResponse)
def create_item(item: TodoCreate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO items (title, description, completed) VALUES (?, ?, ?)",
        (item.title, item.description, item.completed)
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return TodoResponse(id=item_id, **item.dict())

# READ ALL
@app.get("/items", response_model=List[TodoResponse])
def get_items():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed FROM items")
    rows = cursor.fetchall()
    conn.close()
    return [TodoResponse(id=row[0], title=row[1], description=row[2], completed=bool(row[3])) for row in rows]

# READ ONE
@app.get("/items/{item_id}", response_model=TodoResponse)
def get_item(item_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, completed FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return TodoResponse(id=row[0], title=row[1], description=row[2], completed=bool(row[3]))
    raise HTTPException(status_code=404, detail="Item not found")

# UPDATE
@app.put("/items/{item_id}", response_model=TodoResponse)
def update_item(item_id: int, item: TodoCreate):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM items WHERE id = ?", (item_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")
    cursor.execute(
        "UPDATE items SET title = ?, description = ?, completed = ? WHERE id = ?",
        (item.title, item.description, item.completed, item_id)
    )
    conn.commit()
    conn.close()
    return TodoResponse(id=item_id, **item.dict())

# DELETE
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM items WHERE id = ?", (item_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found")
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"detail": f"Item {item_id} deleted"}
