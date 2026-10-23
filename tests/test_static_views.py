# tests/test_static_views.py
"""Test Static Views and Storefront Pages Serving (REQ-F-001, REQ-F-002)."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_homepage_serving():
    """Verify homepage static view is served with 200 OK."""
    response = client.get("/pages/homepage.html")
    assert response.status_code == 200
    assert "Aura" in response.text or "Beauty" in response.text or "Cosmetics" in response.text


def test_product_listing_page_serving():
    """Verify product listing page static view is served."""
    response = client.get("/pages/product-listing.html")
    assert response.status_code == 200
    assert "product" in response.text.lower() or "shade" in response.text.lower()


def test_product_detail_page_serving():
    """Verify product detail page static view is served."""
    response = client.get("/pages/product-detail.html")
    assert response.status_code == 200


def test_cart_page_serving():
    """Verify shopping cart page static view is served."""
    response = client.get("/pages/cart.html")
    assert response.status_code == 200


def test_checkout_page_serving():
    """Verify checkout page static view is served."""
    response = client.get("/pages/checkout.html")
    assert response.status_code == 200


def test_order_confirmation_page_serving():
    """Verify order confirmation page static view is served."""
    response = client.get("/pages/order-confirmation.html")
    assert response.status_code == 200


def test_order_history_page_serving():
    """Verify order history page static view is served."""
    response = client.get("/pages/order-history.html")
    assert response.status_code == 200


def test_returns_page_serving():
    """Verify returns page static view is served."""
    response = client.get("/pages/returns.html")
    assert response.status_code == 200


def test_account_page_serving():
    """Verify account page static view is served."""
    response = client.get("/pages/account.html")
    assert response.status_code == 200
