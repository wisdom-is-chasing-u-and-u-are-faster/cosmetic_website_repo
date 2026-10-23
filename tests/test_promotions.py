# tests/test_promotions.py
"""Test Promotions Engine, Hero Merchandising, and Shade Bundles (REQ-F-005, REQ-F-015)."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_hero_promotions():
    """Verify hero products and shade bundles retrieval (REQ-F-005)."""
    response = client.get("/api/v1/promotions/hero")
    assert response.status_code == 200
    data = response.json()
    assert "hero_products" in data
    assert len(data["hero_products"]) >= 1
    assert "shade_bundles" in data
    assert len(data["shade_bundles"]) >= 2


def test_apply_percentage_promo():
    """Verify valid percentage discount calculation (REQ-F-015)."""
    payload = {
        "code": "GLOW10",
        "cart_total": 100.0,
        "items": []
    }
    response = client.post("/api/v1/promotions/apply", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["discount_amount"] == 10.0
    assert data["final_total"] == 90.0


def test_apply_promo_minimum_spend_failure():
    """Verify promo rejection when minimum spend is not met (REQ-F-015)."""
    payload = {
        "code": "BEAUTY20",  # requires $75 min spend
        "cart_total": 40.0
    }
    response = client.post("/api/v1/promotions/apply", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["title"] == "Minimum Spend Not Met"


def test_apply_invalid_promo_code():
    """Verify 400 error for non-existent promo code."""
    payload = {
        "code": "FAKECODE123",
        "cart_total": 50.0
    }
    response = client.post("/api/v1/promotions/apply", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["title"] == "Invalid Promotional Code"
