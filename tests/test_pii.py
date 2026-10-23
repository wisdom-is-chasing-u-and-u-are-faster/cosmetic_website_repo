# tests/test_pii.py
"""Test GDPR / CCPA Personally Identifiable Information (PII) permanent erasure (REQ-F-012)."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_gdpr_pii_erasure_workflow():
    """Verify customer PII erasure endpoint scrubs customer profile and orders (REQ-F-012)."""
    # Create customer account
    create_payload = {
        "is_guest": False,
        "customer_email": "privacy.user@example.com",
        "customer_name": "Privacy User",
        "shipping_address": {
            "name": "Privacy User",
            "street": "101 Privacy Way",
            "city": "Boston",
            "state": "MA",
            "zip": "02101"
        },
        "payment_method": "Stripe",
        "items": [
            {
                "sku": "VM-01-ROSE",
                "product_id": "prod-vel-matte",
                "product_name": "Velvet Matte Lip",
                "shade_name": "Rose Cashmere",
                "quantity": 1,
                "unit_price": 28.00
            }
        ]
    }
    checkout_res = client.post("/api/v1/checkout/process", json=create_payload)
    assert checkout_res.status_code == 201

    # Call PII erasure
    erasure_res = client.delete(
        "/api/v1/customers/privacy.user@example.com/pii")
    assert erasure_res.status_code == 200
    erasure_data = erasure_res.json()
    assert erasure_data["status"] == "erased"
    assert "anon_" in erasure_data["anonymized_email"]

    # Verify customer email is now anonymized and profile scrubbed
    account_res = client.get(f"/api/v1/account/{erasure_data['customer_id']}")
    assert account_res.status_code == 200
    account_data = account_res.json()
    assert account_data["is_pii_erased"] is True
    assert account_data["full_name"] == "Redacted Customer (GDPR Erased)"
