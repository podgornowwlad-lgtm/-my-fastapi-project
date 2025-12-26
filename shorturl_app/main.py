from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import shortuuid
import database

app = FastAPI()

# Инициализация базы данных
database.init_db()

# Пример эндпоинтов
@app.post("/shorten")
def shorten_url(url: str):
    short_id = shortuuid.uuid()[:6]
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO urls (short_id, full_url) VALUES (?, ?)", (short_id, url))
    conn.commit()
    conn.close()
    return {"short_id": short_id, "short_url": f"http://localhost:8000/{short_id}"}

@app.get("/{short_id}")
def redirect_url(short_id: str):
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT full_url FROM urls WHERE short_id = ?", (short_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return RedirectResponse(url=row[0])
    return {"error": "Short URL not found"}

@app.get("/stats/{short_id}")
def stats(short_id: str):
    conn = sqlite3.connect(database.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT full_url FROM urls WHERE short_id = ?", (short_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"short_id": short_id, "full_url": row[0]}
    return {"error": "Short URL not found"}
