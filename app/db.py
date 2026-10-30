"""
Database Initialization and Connection Layer
Supports SQLite with PostgreSQL DDL compatibility and 12-factor environment variables.
"""

import os
import sqlite3
from pathlib import Path

DB_FILE_PATH = os.getenv("DATABASE_PATH", "skincare_commerce.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE_PATH}")


def get_db_connection() -> sqlite3.Connection:
    """Provides a SQLite connection configured with Row factory for dict-like access."""
    # Handle sqlite:/// URI format
    path = DB_FILE_PATH
    if DATABASE_URL.startswith("sqlite:///"):
        path = DATABASE_URL.replace("sqlite:///", "")

    conn = sqlite3.connect(path, timeout=float(os.getenv("DB_TIMEOUT", "30")))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database() -> None:
    """Executes schema.sql and seed.sql to bootstrap database state."""
    repo_root = Path(__file__).resolve().parent.parent
    schema_path = repo_root / "db" / "schema.sql"
    seed_path = repo_root / "db" / "seed.sql"

    conn = get_db_connection()
    try:
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())

        if seed_path.exists():
            with open(seed_path, "r", encoding="utf-8") as f:
                conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
    print("✅ Database initialized and seeded successfully.")
