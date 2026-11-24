"""
Atomic Inventory Reservation & Stock Control Engine (10-minute hold TTL)
Satisfies REQ-F-001, REQ-F-002, REQ-F-004, REQ-F-005, REQ-F-006, REQ-F-014, REQ-F-015.
Eliminates flash sale overselling and guarantees strict inventory accuracy.
"""

import os
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from app.db import get_db_connection
from app.models import (
    ReservationRequest,
    ReservationResponse,
    ReleaseReservationRequest,
    ReleaseReservationResponse,
    StockStatusResponse,
)

logger = logging.getLogger("inventory_service")
logging.basicConfig(level=logging.INFO)


class InventoryService:
    DEFAULT_TTL_SECONDS = int(os.getenv("INVENTORY_RESERVATION_TTL_SECONDS", "600"))
    LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", "10"))

    @classmethod
    def get_product_stock(cls, product_id_or_sku: str) -> StockStatusResponse:
        """
        Retrieves real-time stock levels for a product or specific SKU.
        Satisfies REQ-F-001 and REQ-F-006.
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            # Try by SKU first
            cursor.execute(
                "SELECT sku, product_id, available_stock, reserved_stock FROM inventory WHERE sku = ?",
                (product_id_or_sku,)
            )
            row = cursor.fetchone()

            # If not found by SKU, check by product_id
            if not row:
                cursor.execute(
                    "SELECT sku, product_id, available_stock, reserved_stock FROM inventory WHERE product_id = ? LIMIT 1",
                    (product_id_or_sku,)
                )
                row = cursor.fetchone()

            if not row:
                # Return out-of-stock response if unknown
                logger.warning(f"Stock record not found for {product_id_or_sku}")
                return StockStatusResponse(
                    sku=product_id_or_sku,
                    product_id=None,
                    available_stock=0,
                    reserved_stock=0,
                    in_stock=False,
                    status="OUT_OF_STOCK",
                    threshold=cls.LOW_STOCK_THRESHOLD
                )

            available = int(row["available_stock"])
            reserved = int(row["reserved_stock"])
            in_stock = available > 0

            if available == 0:
                status = "OUT_OF_STOCK"
            elif available <= cls.LOW_STOCK_THRESHOLD:
                status = "LOW_STOCK"
            else:
                status = "IN_STOCK"

            return StockStatusResponse(
                sku=row["sku"],
                product_id=row["product_id"],
                available_stock=available,
                reserved_stock=reserved,
                in_stock=in_stock,
                status=status,
                threshold=cls.LOW_STOCK_THRESHOLD
            )
        finally:
            conn.close()

    @classmethod
    def reserve_stock(cls, sku: str, quantity: int, session_id: str) -> ReservationResponse:
        """
        Performs atomic reservation with concurrency protection.
        Rejects requests exceeding available stock with ValueError (resulting in HTTP 400).
        Satisfies REQ-F-002, REQ-F-004, REQ-F-006, REQ-F-014, REQ-F-015.
        """
        if quantity <= 0:
            raise ValueError("Reservation quantity must be greater than zero.")

        conn = get_db_connection()
        try:
            cursor = conn.cursor()

            # Atomic transaction check
            cursor.execute(
                "SELECT sku, available_stock, reserved_stock FROM inventory WHERE sku = ?",
                (sku,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"SKU {sku} not found in inventory catalog.")

            available = int(row["available_stock"])
            if available < quantity:
                raise ValueError(
                    f"Insufficient stock for SKU {sku}. Available: {available}, Requested: {quantity}"
                )

            # Atomic decrement and increment
            cursor.execute("""
                UPDATE inventory
                SET available_stock = available_stock - ?,
                    reserved_stock = reserved_stock + ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE sku = ? AND available_stock >= ?
            """, (quantity, quantity, sku, quantity))

            if cursor.rowcount == 0:
                raise ValueError(
                    f"Concurrency lock: Insufficient stock for SKU {sku} during atomic update."
                )

            # Record reservation
            res_id = f"res_{uuid.uuid4().hex[:12]}"
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(seconds=cls.DEFAULT_TTL_SECONDS)
            expires_str = expires_at.isoformat()

            cursor.execute("""
                INSERT INTO inventory_reservations (reservation_id, sku, quantity, session_id, status, expires_at)
                VALUES (?, ?, ?, ?, 'RESERVED', ?)
            """, (res_id, sku, quantity, session_id, expires_str))

            conn.commit()
            logger.info(f"Reserved {quantity} of SKU {sku} (reservation {res_id})")

            return ReservationResponse(
                reservation_id=res_id,
                sku=sku,
                quantity=quantity,
                expires_at=expires_str,
                ttl_seconds=cls.DEFAULT_TTL_SECONDS,
                status="RESERVED"
            )
        finally:
            conn.close()

    @classmethod
    def reserve_inventory(cls, req: ReservationRequest) -> ReservationResponse:
        """Backward-compatible wrapper for ReservationRequest."""
        return cls.reserve_stock(sku=req.sku, quantity=req.quantity, session_id=req.session_id)

    @classmethod
    def release_stock(cls, reservation_id: str) -> ReleaseReservationResponse:
        """
        Releases reserved inventory back to available stock.
        Satisfies REQ-F-006.
        """
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT reservation_id, sku, quantity, status FROM inventory_reservations WHERE reservation_id = ?",
                (reservation_id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Reservation {reservation_id} not found.")

            if row["status"] != "RESERVED":
                return ReleaseReservationResponse(
                    reservation_id=reservation_id,
                    sku=row["sku"],
                    quantity_released=0,
                    status=row["status"]
                )

            sku = row["sku"]
            quantity = int(row["quantity"])

            cursor.execute("""
                UPDATE inventory
                SET available_stock = available_stock + ?,
                    reserved_stock = MAX(0, reserved_stock - ?),
                    last_updated = CURRENT_TIMESTAMP
                WHERE sku = ?
            """, (quantity, quantity, sku))

            cursor.execute("""
                UPDATE inventory_reservations
                SET status = 'RELEASED'
                WHERE reservation_id = ?
            """, (reservation_id,))

            conn.commit()
            logger.info(f"Released {quantity} of SKU {sku} from reservation {reservation_id}")

            return ReleaseReservationResponse(
                reservation_id=reservation_id,
                sku=sku,
                quantity_released=quantity,
                status="RELEASED"
            )
        finally:
            conn.close()
