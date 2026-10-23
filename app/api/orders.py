# app/api/orders.py
"""Order history and real-time 3PL tracking API endpoints (REQ-F-006)."""

import json
import sqlite3
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from app.db.database import get_db
from app.models.schemas import OrderDetailResponse, TrackingEventModel
from app.core.errors import AppException

router = APIRouter(prefix="/api/v1/orders", tags=["Orders"])


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order_by_id_or_number(
        order_id: str, conn: sqlite3.Connection = Depends(get_db)):
    """Fetch order details and real-time 3PL package tracking events (REQ-F-006)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM orders WHERE id = ? OR order_number = ? OR tracking_number = ?
    """, (order_id, order_id, order_id))
    order = cursor.fetchone()

    if not order:
        raise AppException(
            status_code=404,
            title="Order Not Found",
            detail=f"Order with identifier '{order_id}' was not found."
        )

    # Fetch items
    cursor.execute(
        "SELECT * FROM order_items WHERE order_id = ?", (order["id"],))
    items = [dict(i) for i in cursor.fetchall()]

    # Fetch tracking events
    cursor.execute("""
        SELECT timestamp, status, location, description
        FROM tracking_events
        WHERE order_id = ? OR tracking_number = ?
        ORDER BY timestamp ASC
    """, (order["id"], order["tracking_number"]))
    events = [TrackingEventModel(**dict(e)) for e in cursor.fetchall()]

    shipping_dict = json.loads(
        order["shipping_address"]) if order["shipping_address"] else {}

    return OrderDetailResponse(
        id=order["id"],
        order_number=order["order_number"],
        customer_email=order["customer_email"],
        is_guest=bool(order["is_guest"]),
        total_amount=float(order["total_amount"]),
        discount_amount=float(order["discount_amount"] or 0.0),
        promo_code=order["promo_code"],
        payment_method=order["payment_method"],
        payment_status=order["payment_status"],
        tracking_carrier=order["tracking_carrier"] or "FedEx Express",
        tracking_number=order["tracking_number"],
        status=order["status"],
        shipping_address=shipping_dict,
        items=items,
        tracking_events=events,
        created_at=order["created_at"]
    )


@router.get("", response_model=List[OrderDetailResponse])
def list_orders(
    customer_email: Optional[str] = Query(
        None, description="Filter orders by customer email"),
    conn: sqlite3.Connection = Depends(get_db)
):
    """List orders for customer order history (REQ-F-006)."""
    cursor = conn.cursor()
    if customer_email:
        cursor.execute(
            "SELECT * FROM orders WHERE customer_email = ? ORDER BY created_at DESC",
            (customer_email,
             ))
    else:
        cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")

    rows = cursor.fetchall()
    results = []

    for order in rows:
        cursor.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (order["id"],))
        items = [dict(i) for i in cursor.fetchall()]

        cursor.execute(
            """SELECT timestamp, status, location, description
               FROM tracking_events WHERE order_id = ? ORDER BY timestamp ASC""",
            (order["id"],
             ))
        events = [TrackingEventModel(**dict(e)) for e in cursor.fetchall()]

        shipping_dict = json.loads(
            order["shipping_address"]) if order["shipping_address"] else {}

        results.append(
            OrderDetailResponse(
                id=order["id"],
                order_number=order["order_number"],
                customer_email=order["customer_email"],
                is_guest=bool(order["is_guest"]),
                total_amount=float(order["total_amount"]),
                discount_amount=float(order["discount_amount"] or 0.0),
                promo_code=order["promo_code"],
                payment_method=order["payment_method"],
                payment_status=order["payment_status"],
                tracking_carrier=order["tracking_carrier"] or "FedEx Express",
                tracking_number=order["tracking_number"],
                status=order["status"],
                shipping_address=shipping_dict,
                items=items,
                tracking_events=events,
                created_at=order["created_at"]
            )
        )

    return results
