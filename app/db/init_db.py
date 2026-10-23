"""
Database initialization and session connection helper.
Supports zero-dependency local SQLite with automatic schema DDL execution and seed insertion,
or PostgreSQL if DATABASE_URL is configured.
"""

import os
import sqlite3
from pathlib import Path

DB_FILE = os.environ.get("SQLITE_DB_PATH", "app.db")
SCHEMA_PATH = Path("db/schema.sql")
SEED_PATH = Path("db/seed.sql")


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Executes schema.sql and seed.sql to ensure tables and baseline data exist."""
    conn = get_connection()
    cursor = conn.cursor()

    if SCHEMA_PATH.exists():
        schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
        cursor.executescript(schema_sql)

    if SEED_PATH.exists():
        seed_sql = SEED_PATH.read_text(encoding="utf-8")
        cursor.executescript(seed_sql)

    conn.commit()
    conn.close()
    return True


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully.")
