# tests/test_webhooks.py
"""Test Inbound 3PL Webhook Ingestion and HMAC Signature Verification (REQ-F-010)."""

import json
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import generate_hmac_signature, HMAC_SECRET

client = TestClient(app)


def test_3pl_webhook_valid_signature():
    """Verify 3PL webhook processing with valid HMAC SHA256 signature (REQ-F-010)."""
    payload_dict = {
        "event_type": "PACKAGE_IN_TRANSIT",
        "tracking_number": "FDX-7482918234-US",
        "order_id": "ord-1001",
        "status": "In Transit",
        "location": "Regional Hub, Chicago IL",
        "notes": "Departed sort facility"
    }
    raw_bytes = json.dumps(payload_dict).encode("utf-8")
    sig = generate_hmac_signature(raw_bytes, HMAC_SECRET)

    response = client.post(
        "/api/v1/webhooks/3pl",
        content=raw_bytes,
        headers={"Content-Type": "application/json", "X-3PL-Signature": sig}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["received"] is True
    assert data["status"] == "processed"


def test_3pl_webhook_invalid_signature():
    """Verify 401 unauthorized rejection for invalid webhook signature (REQ-F-010)."""
    payload_dict = {
        "event_type": "DELIVERED",
        "tracking_number": "FDX-7482918234-US",
        "status": "Delivered",
        "location": "Front Door"
    }
    raw_bytes = json.dumps(payload_dict).encode("utf-8")

    response = client.post(
        "/api/v1/webhooks/3pl",
        content=raw_bytes,
        headers={"Content-Type": "application/json",
                 "X-3PL-Signature": "invalid_bad_sig"}
    )
    assert response.status_code == 401
    data = response.json()
    assert data["title"] == "Unauthorized Webhook Signature"
