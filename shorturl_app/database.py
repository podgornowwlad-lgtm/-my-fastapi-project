import sqlite3
from pathlib import Path

# Путь к базе данных в томе
DB_PATH = Path("data/shorturls.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            short_id TEXT PRIMARY KEY,
            full_url TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
