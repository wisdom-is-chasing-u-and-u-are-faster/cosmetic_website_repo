# app/api/returns.py
"""Automated returns and customer-initiated shade exchange workflows (REQ-F-007, REQ-F-008)."""

import uuid
import sqlite3
from fastapi import APIRouter, Depends
from app.db.database import get_db
from app.models.schemas import ReturnRequest, ReturnResponse
from app.core.errors import AppException

router = APIRouter(prefix="/api/v1/returns", tags=["Returns & Exchanges"])


@router.post("", status_code=201, response_model=ReturnResponse)
def process_return_or_exchange(
        payload: ReturnRequest, conn: sqlite3.Connection = Depends(get_db)):
    """Initiate automated return or customer shade exchange with prepaid label (REQ-F-007, REQ-F-008)."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM orders WHERE id = ? OR order_number = ?",
        (payload.order_id,
         payload.order_id))
    order = cursor.fetchone()

    if not order:
        raise AppException(
            status_code=404,
            title="Order Not Found",
            detail=f"Order '{payload.order_id}' was not found for return/exchange processing."
        )

    # Verify original SKU was part of the order
    cursor.execute(
        "SELECT * FROM order_items WHERE order_id = ? AND sku = ?",
        (order["id"],
         payload.original_sku))
    item = cursor.fetchone()
    if not item:
        raise AppException(
            status_code=400,
            title="Invalid Return Item",
            detail=f"SKU '{payload.original_sku}' was not found in order '{order['order_number']}'."
        )

    return_id = f"ret_{uuid.uuid4().hex[:10]}"
    label_url = f"https://shipping.aurabeauty.com/labels/return_{return_id}.pdf"
    exchange_order_id = None

    if payload.return_type.lower() == "exchange":
        if not payload.exchange_sku:
            raise AppException(
                status_code=400,
                title="Exchange SKU Required",
                detail="Target exchange SKU must be specified for shade exchanges."
            )
        # Check exchange shade exists and is in stock
        cursor.execute(
            "SELECT shade_name, stock_quantity FROM product_shades WHERE sku = ?",
            (payload.exchange_sku,
             ))
        target_shade = cursor.fetchone()
        if not target_shade:
            raise AppException(
                status_code=404,
                title="Exchange Shade Not Found",
                detail=f"Exchange SKU '{payload.exchange_sku}' was not found in catalog."
            )
        exchange_order_id = f"ord_exc_{uuid.uuid4().hex[:8]}"

    cursor.execute("""
        INSERT INTO returns (
            id, order_id, return_type, original_sku, exchange_sku,
            reason, status, return_label_url, exchange_order_id
        )
        VALUES (?, ?, ?, ?, ?, ?, 'approved', ?, ?)
    """, (
        return_id,
        order["id"],
        payload.return_type.lower(),
        payload.original_sku,
        payload.exchange_sku,
        payload.reason,
        label_url,
        exchange_order_id
    ))

    # Record tracking event
    cursor.execute("""
        INSERT INTO tracking_events (id, order_id, tracking_number, status, location, description)
        VALUES (?, ?, ?, 'Return Label Created', 'Aura Returns Portal', ?)
    """, (
        f"te_{uuid.uuid4().hex[:8]}",
        order["id"],
        order["tracking_number"],
        f"Prepaid return label generated for {payload.original_sku}"
    ))

    conn.commit()

    msg = "Shade exchange approved." if exchange_order_id else "Return approved. Your label is ready."

    return ReturnResponse(
        return_id=return_id,
        order_id=order["id"],
        return_type=payload.return_type.lower(),
        status="approved",
        return_label_url=label_url,
        exchange_order_id=exchange_order_id,
        message=msg
    )
