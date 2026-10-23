# tests/test_orders.py
"""Test Order History and Real-Time 3PL Tracking status (REQ-F-006)."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_order_by_number():
    """Verify order retrieval and tracking events timeline (REQ-F-006)."""
    response = client.get("/api/v1/orders/ORD-98214-AUR")
    assert response.status_code == 200
    data = response.json()
    assert data["order_number"] == "ORD-98214-AUR"
    assert data["customer_email"] == "guest@example.com"
    assert len(data["items"]) >= 2
    assert len(data["tracking_events"]) >= 4
    event_statuses = [e["status"] for e in data["tracking_events"]]
    assert "Delivered" in event_statuses or "In Transit" in event_statuses or "Order Placed" in event_statuses


def test_list_orders_by_customer_email():
    """Verify order list filtered by customer email."""
    response = client.get("/api/v1/orders?customer_email=guest@example.com")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(o["order_number"] == "ORD-98214-AUR" for o in data)


def test_order_not_found():
    """Verify 404 for non-existent order query."""
    response = client.get("/api/v1/orders/NON-EXISTENT-ORDER")
    assert response.status_code == 404
    data = response.json()
    assert data["title"] == "Order Not Found"
