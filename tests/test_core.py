# tests/test_core.py
"""Test Core Errors (RFC-7807), Idempotency, and Security HMAC utilities (REQ-F-010, REQ-F-013, REQ-F-014)."""

import uuid
import pytest
from app.core.errors import AppException, create_problem_response
from app.core.security import generate_hmac_signature, verify_hmac_signature, anonymize_pii_string
from app.core.idempotency import IdempotencyManager
from app.db.database import get_connection, init_database

def test_rfc7807_problem_response():
    """Verify RFC-7807 problem details response formatting."""
    resp = create_problem_response(
        status_code=400,
        title="Invalid Parameter",
        detail="The requested shade is out of stock.",
        instance="/api/v1/checkout/reserve"
    )
    assert resp.status_code == 400
    assert resp.media_type == "application/problem+json"

def test_hmac_signature_verification():
    """Verify HMAC SHA256 signature generation and verification for 3PL webhooks."""
    payload = b'{"event_type": "DELIVERED", "tracking_number": "FDX-12345"}'
    signing_token = "dummy_test_token_val_12345"
    sig = generate_hmac_signature(payload, signing_token)

    assert verify_hmac_signature(payload, sig, signing_token) is True
    assert verify_hmac_signature(payload, f"sha256={sig}", signing_token) is True
    assert verify_hmac_signature(payload, "invalid_sig", signing_token) is False

def test_pii_anonymization():
    """Verify deterministic GDPR PII anonymization mask."""
    email = "jane.doe@example.com"
    anon = anonymize_pii_string(email)
    assert anon.startswith("anon_")
    assert "@redacted.local" in anon
    assert anon == anonymize_pii_string(email)

def test_idempotency_manager():
    """Verify IdempotencyManager storage and replay."""
    conn = get_connection()
    key = f"idem-test-key-{uuid.uuid4().hex}"

    assert IdempotencyManager.get_record(conn, key) is None

    payload = {"order_id": "ord_123", "status": "confirmed"}
    IdempotencyManager.save_record(conn, key, 201, payload)

    cached = IdempotencyManager.get_record(conn, key)
    assert cached is not None
    assert cached[0] == 201
    assert cached[1]["order_id"] == "ord_123"
    conn.close()
