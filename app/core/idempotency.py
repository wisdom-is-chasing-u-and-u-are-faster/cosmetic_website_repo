# app/core/idempotency.py
"""Idempotency management for mutating API endpoints (REQ-F-013)."""

import json
import sqlite3
from typing import Optional, Tuple, Dict, Any


class IdempotencyManager:
    """Manages transactional idempotency using database storage."""

    @staticmethod
    def get_record(conn: sqlite3.Connection,
                   key: str) -> Optional[Tuple[int, Dict[str, Any]]]:
        """Fetch previously recorded response for an idempotency key."""
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status_code, response_body FROM idempotency_records WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            try:
                body = json.loads(row["response_body"])
            except Exception:
                body = {"data": row["response_body"]}
            return row["status_code"], body
        return None

    @staticmethod
    def save_record(conn: sqlite3.Connection, key: str,
                    status_code: int, response_body: Any):
        """Save executed response for an idempotency key."""
        cursor = conn.cursor()
        body_str = json.dumps(response_body) if not isinstance(
            response_body, str) else response_body
        cursor.execute(
            "INSERT OR REPLACE INTO idempotency_records (key, status_code, response_body) VALUES (?, ?, ?)",
            (key, status_code, body_str)
        )
        conn.commit()
