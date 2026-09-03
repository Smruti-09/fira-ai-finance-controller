import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("../data/audit_logs.db")

def init_audit_db():
    DB_PATH.parent.mkdir(exist_ok=True, parents=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            order_id TEXT,
            action TEXT,
            status TEXT,
            user TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_audit_event(order_id: str, action: str, status: str, user: str = "AI_Controller_Bot"):
    init_audit_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO audit_logs (timestamp, order_id, action, status, user)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, order_id, action, status, user))
    conn.commit()
    conn.close()

def get_all_audit_logs():
    init_audit_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]