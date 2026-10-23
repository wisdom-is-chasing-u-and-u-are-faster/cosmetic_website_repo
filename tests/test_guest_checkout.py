# tests/test_guest_checkout.py
"""Test Optimized Guest Checkout Flow without Mandatory Registration (REQ-F-004)."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_guest_checkout_flow():
    """Verify that a guest user can place an order without account creation (REQ-F-004)."""
    payload = {
        "is_guest": True,
        "customer_email": "first.time.guest@example.com",
        "customer_name": "First Time Guest",
        "shipping_address": {
            "name": "First Time Guest",
            "street": "500 Pine St",
            "city": "Seattle",
            "state": "WA",
            "zip": "98101",
            "country": "USA"
        },
        "payment_method": "Google Pay",
        "payment_token": "tok_gpay_mock",
        "items": [
            {
                "sku": "HG-01-FAIR",
                "product_id": "prod-hydra-glow",
                "product_name": "Hydra-Glow Multi-Use Concealer",
                "shade_name": "Fair 01 Neutral",
                "quantity": 1,
                "unit_price": 32.00
            }
        ]
    }
    response = client.post("/api/v1/checkout/process", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "confirmed"
    assert data["total_amount"] == 32.00
    assert "tracking_number" in data

    # Verify order can be retrieved directly via order number by guest
    order_res = client.get(f"/api/v1/orders/{data['order_number']}")
    assert order_res.status_code == 200
    order_data = order_res.json()
    assert order_data["is_guest"] is True
    assert order_data["customer_email"] == "first.time.guest@example.com"
