# tests/test_returns.py
"""Test Customer-Initiated Shade Exchange and Automated Return Processing (REQ-F-007, REQ-F-008)."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_automated_return_processing():
    """Verify automated standard return initiation with prepaid label (REQ-F-008)."""
    payload = {
        "order_id": "ORD-98214-AUR",
        "return_type": "return",
        "original_sku": "LS-30-NEUT",
        "reason": "Texture does not match preference"
    }
    response = client.post("/api/v1/returns", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "approved"
    assert "return_id" in data
    assert "return_label_url" in data
    assert "labels/return_" in data["return_label_url"]


def test_customer_initiated_shade_exchange():
    """Verify customer-initiated shade exchange workflow (REQ-F-007)."""
    # Note: the API expects `exchange_sku`
    payload_correct = {
        "order_id": "ORD-98214-AUR",
        "return_type": "exchange",
        "original_sku": "LS-30-NEUT",
        "exchange_sku": "LS-20-WARM",
        "reason": "Shade was slightly too deep for winter skin tone"
    }
    response = client.post("/api/v1/returns", json=payload_correct)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "approved"
    assert data["return_type"] == "exchange"
    assert data["exchange_order_id"] is not None
    assert "Shade exchange approved" in data["message"]


def test_return_invalid_sku():
    """Verify error when attempting to return a SKU not present in order."""
    payload = {
        "order_id": "ORD-98214-AUR",
        "return_type": "return",
        "original_sku": "NON-EXISTENT-SKU",
        "reason": "Wrong item"
    }
    response = client.post("/api/v1/returns", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["title"] == "Invalid Return Item"
