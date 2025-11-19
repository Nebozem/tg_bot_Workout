import sqlite3
from datetime import datetime

DB_PATH = "data/db.sqlite"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            exercise TEXT,
            weight REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_weight(user_id: int, exercise: str, weight: float):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO weights (user_id, exercise, weight, date) VALUES (?, ?, ?, ?)",
        (user_id, exercise, weight, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_last_weight(user_id: int, exercise: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT weight FROM weights WHERE user_id=? AND exercise=? ORDER BY id DESC LIMIT 1",
        (user_id, exercise)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def get_weight_history(user_id: int, exercise: str):
    """Получает всю историю весов для упражнения"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT weight, date FROM weights WHERE user_id=? AND exercise=? ORDER BY date DESC",
        (user_id, exercise)
    )
    history = cursor.fetchall()
    conn.close()
    return history