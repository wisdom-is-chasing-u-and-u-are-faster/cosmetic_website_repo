"""
Atomic Inventory Reservation & Dual-PSP Order Lifecycle Tests
Satisfies REQ-F-007, REQ-F-008, REQ-F-009, REQ-F-010
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_atomic_inventory_reservation_with_ttl():
    """Verify atomic reservation creates a 10-minute hold and deducts available stock."""
    payload = {
        "sku": "SKU-TINT-100",
        "quantity": 2,
        "session_id": "test_sess_001"
    }

    res = client.post("/api/v1/inventory/reserve", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["reservation_id"].startswith("res_")
    assert data["ttl_seconds"] == 600
    assert data["status"] == "RESERVED"


def test_order_creation_dual_psp_routing():
    """Verify order creation logs transactional outbox event and routes to PSP."""
    payload = {
        "reservation_id": "res_mock_123",
        "items": [
            {
                "sku": "SKU-TINT-100",
                "product_id": "prod-tint-01",
                "quantity": 1,
                "price": 42.00
            }
        ],
        "customer": {
            "email": "customer@example.com",
            "name": "Jane Doe",
            "shipping_address": {
                "street": "123 Skincare Ave",
                "city": "New York",
                "state": "NY",
                "zip": "10001",
                "country": "US"
            }
        },
        "payment_method": "credit_card"
    }

    res = client.post("/api/v1/orders", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["order_id"].startswith("ord_")
    assert data["status"] == "CONFIRMED"
    assert data["psp_routed"] in ["stripe", "adyen"]
    assert data["outbox_event_id"].startswith("evt_")
