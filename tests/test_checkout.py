# tests/test_checkout.py
"""Test Inventory Reservation Locks and Single-Page Progressive Checkout."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_inventory_reservation_success():
    """Verify real-time inventory reservation lock acquisition (REQ-F-009)."""
    payload = {
        "items": [
            {"sku": "LS-10-COOL", "quantity": 2}
        ],
        "reservation_ttl_seconds": 600
    }
    response = client.post("/api/v1/checkout/reserve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reservation_id" in data
    assert data["status"] == "reserved"


def test_inventory_reservation_insufficient_stock():
    """Verify inventory lock rejection when requested quantity exceeds stock (REQ-F-009)."""
    payload = {
        "items": [
            {"sku": "LS-10-COOL", "quantity": 9999}
        ]
    }
    response = client.post("/api/v1/checkout/reserve", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["title"] == "Insufficient Inventory"


def test_checkout_process_stripe_payment():
    """Verify single-page progressive checkout order processing (REQ-F-002, REQ-F-003)."""
    payload = {
        "is_guest": True,
        "customer_email": "guest.buyer@test.com",
        "customer_name": "Guest Buyer",
        "shipping_address": {
            "name": "Guest Buyer",
            "street": "123 Fifth Ave",
            "city": "New York",
            "state": "NY",
            "zip": "10001",
            "country": "USA"
        },
        "payment_method": "Stripe",
        "payment_token": "tok_visa",
        "promo_code": "GLOW10",
        "items": [
            {
                "sku": "LS-10-COOL",
                "product_id": "prod-lum-silk",
                "product_name": "Luminous Silk Foundation",
                "shade_name": "1.0 Fair Alabaster",
                "quantity": 1,
                "unit_price": 48.00
            }
        ]
    }
    response = client.post("/api/v1/checkout/process", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "order_id" in data
    assert "order_number" in data
    assert data["status"] == "confirmed"
    assert data["total_amount"] == 43.20  # 48.00 - 10%
    assert data["discount_amount"] == 4.80
    assert "tracking_number" in data


def test_checkout_idempotency_key_replay():
    """Verify transaction replay safety with Idempotency-Key header (REQ-F-013)."""
    headers = {"Idempotency-Key": "idem-checkout-test-999"}
    payload = {
        "is_guest": True,
        "customer_email": "idem.user@test.com",
        "shipping_address": {
            "name": "Idem User",
            "street": "100 Broadway",
            "city": "New York",
            "state": "NY",
            "zip": "10001"
        },
        "payment_method": "Apple Pay",
        "items": [
            {
                "sku": "VM-01-ROSE",
                "product_id": "prod-vel-matte",
                "product_name": "Velvet Matte Liquid Lip",
                "shade_name": "Rose Cashmere",
                "quantity": 1,
                "unit_price": 28.00
            }
        ]
    }
    res1 = client.post(
        "/api/v1/checkout/process",
        json=payload,
        headers=headers)
    assert res1.status_code == 201
    data1 = res1.json()

    # Replay identical request with same idempotency key
    res2 = client.post(
        "/api/v1/checkout/process",
        json=payload,
        headers=headers)
    assert res2.status_code == 201
    data2 = res2.json()

    assert data1["order_id"] == data2["order_id"]
    assert data1["order_number"] == data2["order_number"]
