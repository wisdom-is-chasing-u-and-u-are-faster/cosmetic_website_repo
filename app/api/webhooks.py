# app/api/webhooks.py
"""Asynchronous 3PL logistics webhook ingestion with HMAC signature verification (REQ-F-010)."""

import uuid
import json
import sqlite3
from typing import Optional
from fastapi import APIRouter, Depends, Header, Request
from app.db.database import get_db
from app.models.schemas import Webhook3PLPayload, WebhookResponse
from app.core.errors import AppException
from app.core.security import verify_hmac_signature

router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks & Logistics"])


@router.post("/3pl", response_model=WebhookResponse)
async def ingest_3pl_webhook(
    request: Request,
    x_3pl_signature: Optional[str] = Header(None, alias="X-3PL-Signature"),
    x_signature: Optional[str] = Header(None, alias="X-Signature"),
    conn: sqlite3.Connection = Depends(get_db)
):
    """Inbound 3PL fulfillment dispatcher endpoint verifying HMAC SHA256 signatures (REQ-F-010)."""
    raw_body = await request.body()
    sig = x_3pl_signature or x_signature

    if not sig or not verify_hmac_signature(raw_body, sig):
        raise AppException(
            status_code=401,
            title="Unauthorized Webhook Signature",
            detail="Invalid or missing HMAC SHA256 signature in X-3PL-Signature header."
        )

    try:
        data = json.loads(raw_body.decode("utf-8"))
        payload = Webhook3PLPayload(**data)
    except Exception as e:
        raise AppException(
            status_code=400,
            title="Malformed Webhook Payload",
            detail=f"Unable to parse 3PL payload: {str(e)}"
        )

    cursor = conn.cursor()

    # Find associated order
    order_id = payload.order_id
    if not order_id:
        cursor.execute(
            "SELECT id FROM orders WHERE tracking_number = ?",
            (payload.tracking_number,
             ))
        row = cursor.fetchone()
        if row:
            order_id = row["id"]

    event_id = f"evt_{uuid.uuid4().hex[:10]}"

    if order_id:
        cursor.execute("""
            INSERT INTO tracking_events (id, order_id, tracking_number, status, location, description)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            order_id,
            payload.tracking_number,
            payload.status,
            payload.location,
            payload.notes or f"3PL tracking update: {payload.status} at {payload.location}"
        ))

        # Update order status if delivered or shipped
        if payload.status.lower() in [
                "delivered", "shipped", "out for delivery", "in transit"]:
            normalized_status = payload.status.lower().replace(" ", "_")
            cursor.execute(
                "UPDATE orders SET status = ? WHERE id = ?",
                (normalized_status,
                 order_id))

    conn.commit()

    return WebhookResponse(
        received=True,
        event_id=event_id,
        status="processed"
    )
