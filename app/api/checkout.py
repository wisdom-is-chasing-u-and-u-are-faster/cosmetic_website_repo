# app/api/checkout.py
"""Inventory reservation and single-page checkout endpoints."""

import uuid
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Header
from app.db.database import get_db
from app.models.schemas import (
    InventoryReserveRequest,
    InventoryReserveResponse,
    CheckoutProcessRequest,
    CheckoutProcessResponse
)
from app.core.errors import AppException
from app.core.idempotency import IdempotencyManager

router = APIRouter(prefix="/api/v1/checkout", tags=["Checkout"])


@router.post("/reserve", response_model=InventoryReserveResponse)
def reserve_inventory(
    payload: InventoryReserveRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    conn: sqlite3.Connection = Depends(get_db)
):
    """Acquire real-time inventory reservation lock during checkout to prevent overselling (REQ-F-009, REQ-F-013)."""
    if idempotency_key:
        cached = IdempotencyManager.get_record(conn, idempotency_key)
        if cached:
            return InventoryReserveResponse(**cached[1])

    cursor = conn.cursor()
    reservation_id = f"res_{uuid.uuid4().hex[:12]}"
    expires_at = (datetime.utcnow() + timedelta(seconds=payload.reservation_ttl_seconds)).isoformat() + "Z"

    # Verify inventory availability
    for item in payload.items:
        cursor.execute("SELECT stock_quantity, shade_name FROM product_shades WHERE sku = ?", (item.sku,))
        shade = cursor.fetchone()
        if not shade:
            raise AppException(
                status_code=404,
                title="SKU Not Found",
                detail=f"Product shade variant with SKU '{item.sku}' does not exist."
            )
        if shade["stock_quantity"] < item.quantity:
            raise AppException(
                status_code=409,
                title="Insufficient Inventory",
                detail=f"Requested qty ({item.quantity}) exceeds stock for '{shade['shade_name']}'."
            )

    # Insert reservation records
    for item in payload.items:
        cursor.execute("""
            INSERT INTO inventory_reservations (reservation_id, sku, quantity, status, expires_at, idempotency_key)
            VALUES (?, ?, ?, 'active', ?, ?)
        """, (reservation_id, item.sku, item.quantity, expires_at, idempotency_key))

    conn.commit()

    resp = InventoryReserveResponse(
        reservation_id=reservation_id,
        status="reserved",
        expires_at=expires_at,
        items_reserved=len(payload.items)
    )

    if idempotency_key:
        IdempotencyManager.save_record(conn, idempotency_key, 200, resp.model_dump())

    return resp


@router.post("/process", status_code=201, response_model=CheckoutProcessResponse)
def process_checkout(
    payload: CheckoutProcessRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    conn: sqlite3.Connection = Depends(get_db)
):
    """Execute single-page progressive checkout with Stripe/Wallet integration and guest support."""
    if idempotency_key:
        cached = IdempotencyManager.get_record(conn, idempotency_key)
        if cached:
            return CheckoutProcessResponse(**cached[1])

    if not payload.items:
        raise AppException(
            status_code=400,
            title="Empty Cart",
            detail="Cannot execute checkout with an empty cart."
        )

    cursor = conn.cursor()

    # Calculate totals
    subtotal = sum(item.unit_price * item.quantity for item in payload.items)
    discount_amount = 0.0

    # Validate promo code if provided
    if payload.promo_code:
        cursor.execute("SELECT * FROM promotions WHERE UPPER(code) = ? AND is_active = 1",
                       (payload.promo_code.upper(),))
        promo = cursor.fetchone()
        if promo:
            if promo["discount_type"] == "percentage":
                discount_amount = round(subtotal * (float(promo["discount_value"]) / 100.0), 2)
            else:
                discount_amount = min(float(promo["discount_value"]), subtotal)

    total_amount = max(0.0, round(subtotal - discount_amount, 2))

    # Payment simulation (Stripe / Apple Pay / Google Pay)
    valid_payment_methods = ["Stripe", "Apple Pay", "Google Pay", "Credit Card"]
    if payload.payment_method not in valid_payment_methods:
        raise AppException(
            status_code=400,
            title="Invalid Payment Method",
            detail=f"Payment method '{payload.payment_method}' is not supported. Supported: {valid_payment_methods}"
        )

    order_id = f"ord_{uuid.uuid4().hex[:10]}"
    order_number = f"ORD-{uuid.uuid4().hex[:5].upper()}-AUR"
    tracking_number = f"FDX-{uuid.uuid4().hex[:10].upper()}-US"
    deliv_date = datetime.utcnow() + timedelta(days=3)
    estimated_delivery = deliv_date.strftime("%A, %B %d, %Y")

    shipping_json = json.dumps(payload.shipping_address.model_dump())
    billing_json = json.dumps(payload.billing_address.model_dump()) if payload.billing_address else shipping_json

    customer_id = None
    if not payload.is_guest:
        cursor.execute("SELECT id FROM customers WHERE email = ?", (payload.customer_email,))
        c_row = cursor.fetchone()
        if c_row:
            customer_id = c_row["id"]
        else:
            customer_id = f"cust_{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO customers (id, email, full_name, is_pii_erased)
                VALUES (?, ?, ?, 0)
            """, (customer_id, payload.customer_email, payload.customer_name or "Valued Customer"))

    # 1. Insert order FIRST
    cursor.execute("""
        INSERT INTO orders (
            id, order_number, customer_id, customer_email, is_guest,
            total_amount, discount_amount, promo_code, payment_method,
            payment_status, tracking_carrier, tracking_number, status,
            shipping_address, billing_address
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        order_id,
        order_number,
        customer_id,
        payload.customer_email,
        1 if payload.is_guest else 0,
        total_amount,
        discount_amount,
        payload.promo_code,
        payload.payment_method,
        "succeeded",
        "FedEx Express",
        tracking_number,
        "confirmed",
        shipping_json,
        billing_json
    ))

    # 2. Decrement stock and insert order items
    for item in payload.items:
        cursor.execute("SELECT stock_quantity FROM product_shades WHERE sku = ?", (item.sku,))
        shade = cursor.fetchone()
        if shade:
            new_qty = max(0, shade["stock_quantity"] - item.quantity)
            cursor.execute("UPDATE product_shades SET stock_quantity = ? WHERE sku = ?", (new_qty, item.sku))

        cursor.execute("""
            INSERT INTO order_items (id, order_id, sku, product_name, shade_name, quantity, unit_price, subtotal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f"oi_{uuid.uuid4().hex[:8]}",
            order_id,
            item.sku,
            item.product_name,
            item.shade_name,
            item.quantity,
            item.unit_price,
            round(item.unit_price * item.quantity, 2)
        ))

    # 3. Initial 3PL tracking event
    cursor.execute("""
        INSERT INTO tracking_events (id, order_id, tracking_number, status, location, description, timestamp)
        VALUES (?, ?, ?, 'Order Placed', 'Aura Fulfillment Center', 'Order verified for fulfillment', ?)
    """, (f"te_{uuid.uuid4().hex[:8]}", order_id, tracking_number, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

    # Convert reservation if used
    if payload.reservation_id:
        cursor.execute("UPDATE inventory_reservations SET status = 'converted' WHERE reservation_id = ?",
                       (payload.reservation_id,))

    conn.commit()

    resp = CheckoutProcessResponse(
        order_id=order_id,
        order_number=order_number,
        status="confirmed",
        total_amount=total_amount,
        discount_amount=discount_amount,
        tracking_carrier="FedEx Express",
        tracking_number=tracking_number,
        estimated_delivery=estimated_delivery,
        message="Order successfully placed via single-page checkout."
    )

    if idempotency_key:
        IdempotencyManager.save_record(conn, idempotency_key, 201, resp.model_dump())

    return resp
