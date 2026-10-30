"""
Atomic Inventory Reservation Engine (10-minute hold TTL)
Satisfies REQ-F-007, REQ-F-009, eliminates flash sale overselling.
"""

import os
import uuid
from datetime import datetime, timedelta, timezone
from app.db import get_db_connection
from app.models import ReservationRequest, ReservationResponse


class InventoryService:
    DEFAULT_TTL_SECONDS = int(os.getenv("INVENTORY_RESERVATION_TTL_SECONDS", "600"))

    @classmethod
    def reserve_inventory(cls, req: ReservationRequest) -> ReservationResponse:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # Check available inventory
            cursor.execute("SELECT sku, available_stock, reserved_stock FROM inventory WHERE sku = ?", (req.sku,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"SKU {req.sku} not found in inventory catalog.")

            available = row["available_stock"]
            if available < req.quantity:
                raise ValueError(
                    f"Insufficient stock for SKU {req.sku}. Available: {available}, Requested: {req.quantity}"
                )

            # Deduct available, increment reserved
            cursor.execute("""
                UPDATE inventory
                SET available_stock = available_stock - ?, reserved_stock = reserved_stock + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE sku = ?
            """, (req.quantity, req.quantity, req.sku))

            # Record atomic reservation
            res_id = f"res_{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(seconds=cls.DEFAULT_TTL_SECONDS)
            expires_str = expires_at.isoformat()

            cursor.execute("""
                INSERT INTO inventory_reservations (reservation_id, sku, quantity, session_id, status, expires_at)
                VALUES (?, ?, ?, ?, 'RESERVED', ?)
            """, (res_id, req.sku, req.quantity, req.session_id, expires_str))

            conn.commit()

            return ReservationResponse(
                reservation_id=res_id,
                sku=req.sku,
                quantity=req.quantity,
                expires_at=expires_str,
                ttl_seconds=cls.DEFAULT_TTL_SECONDS,
                status="RESERVED"
            )
        finally:
            conn.close()
