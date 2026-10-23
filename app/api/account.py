# app/api/account.py
"""Customer account profile management and GDPR/CCPA PII erasure endpoints (REQ-F-012)."""

import uuid
import sqlite3
from fastapi import APIRouter, Depends
from app.db.database import get_db
from app.models.schemas import CustomerAccountResponse, CustomerUpdateRequest, PIIErasureResponse
from app.core.errors import AppException

router = APIRouter(tags=["Account & Privacy"])


@router.get("/api/v1/account/{customer_id}",
            response_model=CustomerAccountResponse)
def get_customer_account(customer_id: str,
                         conn: sqlite3.Connection = Depends(get_db)):
    """Fetch customer profile and shade preferences."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM customers WHERE id = ? OR email = ?",
        (customer_id,
         customer_id))
    cust = cursor.fetchone()

    if not cust:
        raise AppException(
            status_code=404,
            title="Customer Profile Not Found",
            detail=f"Customer with ID/email '{customer_id}' was not found."
        )

    return CustomerAccountResponse(
        id=cust["id"],
        email=cust["email"],
        full_name=cust["full_name"],
        phone=cust["phone"],
        skin_tone_profile=cust["skin_tone_profile"],
        undertone_profile=cust["undertone_profile"],
        is_pii_erased=bool(cust["is_pii_erased"])
    )


@router.put("/api/v1/account/{customer_id}",
            response_model=CustomerAccountResponse)
def update_customer_account(customer_id: str, payload: CustomerUpdateRequest,
                            conn: sqlite3.Connection = Depends(get_db)):
    """Update customer profile information and shade preferences."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM customers WHERE id = ? OR email = ?",
        (customer_id,
         customer_id))
    cust = cursor.fetchone()

    if not cust:
        raise AppException(
            status_code=404,
            title="Customer Profile Not Found",
            detail=f"Customer with ID/email '{customer_id}' was not found."
        )

    cid = cust["id"]
    new_name = payload.full_name if payload.full_name is not None else cust["full_name"]
    new_phone = payload.phone if payload.phone is not None else cust["phone"]
    new_st = payload.skin_tone_profile if payload.skin_tone_profile is not None else cust[
        "skin_tone_profile"]
    new_ut = payload.undertone_profile if payload.undertone_profile is not None else cust[
        "undertone_profile"]

    cursor.execute("""
        UPDATE customers
        SET full_name = ?, phone = ?, skin_tone_profile = ?, undertone_profile = ?
        WHERE id = ?
    """, (new_name, new_phone, new_st, new_ut, cid))
    conn.commit()

    return CustomerAccountResponse(
        id=cid,
        email=cust["email"],
        full_name=new_name,
        phone=new_phone,
        skin_tone_profile=new_st,
        undertone_profile=new_ut,
        is_pii_erased=bool(cust["is_pii_erased"])
    )


@router.delete("/api/v1/customers/{customer_id}/pii",
               response_model=PIIErasureResponse)
def erase_customer_pii(customer_id: str,
                       conn: sqlite3.Connection = Depends(get_db)):
    """GDPR / CCPA compliant Personally Identifiable Information (PII) permanent erasure (REQ-F-012)."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM customers WHERE id = ? OR email = ?",
        (customer_id,
         customer_id))
    cust = cursor.fetchone()

    if not cust:
        raise AppException(
            status_code=404,
            title="Customer Record Not Found",
            detail=f"Customer with identifier '{customer_id}' was not found."
        )

    cid = cust["id"]
    orig_email = cust["email"]
    anon_email = f"anon_{uuid.uuid4().hex[:12]}@redacted.local"
    anon_name = "Redacted Customer (GDPR Erased)"

    # Anonymize customer table
    cursor.execute("""
        UPDATE customers
        SET email = ?, full_name = ?, phone = NULL,
            skin_tone_profile = NULL, undertone_profile = NULL, is_pii_erased = 1
        WHERE id = ?
    """, (anon_email, anon_name, cid))

    # Anonymize associated orders
    cursor.execute("""
        UPDATE orders
        SET customer_email = ?, shipping_address = '{"redacted": true, "reason": "GDPR/CCPA PII erasure"}'
        WHERE customer_id = ? OR customer_email = ?
    """, (anon_email, cid, orig_email))

    # Log audit trail (without PII)
    cursor.execute("""
        INSERT INTO audit_logs (id, event_type, entity_id, details)
        VALUES (?, 'GDPR_PII_ERASURE', ?, 'Customer requested full PII erasure; all data scrubbed and anonymized.')
    """, (f"audit_{cid}_{uuid.uuid4().hex[:6]}", cid))

    conn.commit()

    return PIIErasureResponse(
        customer_id=cid,
        status="erased",
        anonymized_email=anon_email,
        message="All PII has been permanently erased in compliance with GDPR/CCPA."
    )
