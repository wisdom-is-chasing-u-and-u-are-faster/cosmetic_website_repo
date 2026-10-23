# app/db/database.py
"""Database connection and initialization module supporting SQLite and PostgreSQL parity."""

import os
import sqlite3
from pathlib import Path
from typing import Optional

DB_FILE = os.getenv("DATABASE_FILE", "cosmetics_store.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE}")


def get_connection() -> sqlite3.Connection:
    """Return a configured sqlite3 connection with Row factory."""
    # Strip sqlite:/// prefix if present
    db_path = DATABASE_URL.replace(
        "sqlite:///",
        "") if DATABASE_URL.startswith("sqlite:///") else DB_FILE
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def get_db():
    """Dependency generator for FastAPI routes."""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_database(
        schema_path: Optional[str] = None, seed_path: Optional[str] = None):
    """Initialize database tables and baseline seed data."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    s_path = Path(schema_path) if schema_path else base_dir / \
        "db" / "schema.sql"
    d_path = Path(seed_path) if seed_path else base_dir / "db" / "seed.sql"

    conn = get_connection()
    try:
        with conn:
            if s_path.exists():
                conn.executescript(s_path.read_text(encoding="utf-8"))
            if d_path.exists():
                conn.executescript(d_path.read_text(encoding="utf-8"))
    finally:
        conn.close()


def close_db():
    """Cleanly close database resources if needed."""
    pass
