"""
Minimal SQLite logging layer -- zero setup, no external database needed.
Every routed request gets logged here for the dashboard to display.
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "logs.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            prompt TEXT,
            model_used TEXT,
            complexity TEXT,
            latency_seconds REAL,
            total_tokens INTEGER,
            estimated_cost_usd REAL
        )
    """)
    conn.commit()
    conn.close()


def log_request(prompt: str, result: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO requests
        (timestamp, prompt, model_used, complexity, latency_seconds, total_tokens, estimated_cost_usd)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        prompt,
        result["model_used"],
        result["complexity"],
        result["latency_seconds"],
        result["total_tokens"],
        result["estimated_cost_usd"],
    ))
    conn.commit()
    conn.close()


def get_all_requests(limit: int = 50):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, prompt, model_used, complexity, latency_seconds, total_tokens, estimated_cost_usd
        FROM requests
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows
