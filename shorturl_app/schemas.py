from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl
from typing import Dict
import database
import shortuuid
from datetime import datetime

app = FastAPI(title="URL Shortener Service", version="1.0.0")

# Инициализация базы данных при запуске
database.init_db()

class ShortenRequest(BaseModel):
    url: str

class ShortenResponse(BaseModel):
    short_id: str
    short_url: str

class StatsResponse(BaseModel):
    short_id: str
    original_url: str
    created_at: str
    access_count: int

@app.post("/shorten", response_model=ShortenResponse, status_code=201)
def shorten_url(request: ShortenRequest):
    # Генерируем короткий идентификатор
    short_id = shortuuid.ShortUUID().random(length=6)
    
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Проверяем, не существует ли уже такой short_id
    while True:
        cursor.execute("SELECT id FROM short_urls WHERE id = ?", (short_id,))
        if not cursor.fetchone():
            break
        short_id = shortuuid.ShortUUID().random(length=6)
    
    # Сохраняем в базу данных
    cursor.execute(
        "INSERT INTO short_urls (id, original_url) VALUES (?, ?)",
        (short_id, str(request.url))
    )
    
    conn.commit()
    conn.close()
    
    return {
        "short_id": short_id,
        "short_url": f"/{short_id}"
    }

@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    conn = database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT original_url FROM short_urls WHERE id = ?",
        (short_id,)
    )
    
    row = cursor.fetchone()
    
    if row:
        # Увеличиваем счетчик доступа
        cursor.execute(
            "UPDATE short_urls SET access_count = access_count + 1 WHERE id = ?",
            (short_id,)
        )
        conn.commit()
        conn.close()
        
        # Перенаправляем на оригинальный URL
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=row[0], status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    
    conn.close()
    raise HTTPException(status_code=404, detail="Short URL not found")

@app.get("/stats/{short_id}", response_model=StatsResponse)
def get_url_stats(short_id: str):
    conn = database.get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, original_url, created_at, access_count FROM short_urls WHERE id = ?",
        (short_id,)
    )
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "short_id": row[0],
            "original_url": row[1],
            "created_at": row[2],
            "access_count": row[3]
        }
    
    raise HTTPException(status_code=404, detail="Short URL not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)