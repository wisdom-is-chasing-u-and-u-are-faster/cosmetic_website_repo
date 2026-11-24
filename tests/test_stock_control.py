"""
Unit, Integration, and Concurrency Test Suite for Product Availability & Stock Control (ARCH-10099)
Validates REQ-F-001 through REQ-F-015:
- Real-time stock visibility
- Clamping of quantities to available stock
- Atomic reservations rejecting requests > available stock with HTTP 400
- Out-of-stock and low-stock states
- Dedicated Inventory Service operations (get_product_stock, reserve_stock, release_stock)
"""

import pytest
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from app.main import app
from app.services.inventory_service import InventoryService
from app.models import ReservationRequest, ReleaseReservationRequest
from app.db import get_db_connection, init_database


@pytest.fixture(autouse=True)
def setup_test_db():
    """Ensure database is seeded prior to each test run."""
    init_database()
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_product_detail_includes_stock_status_and_quantity(client):
    """
    AC: The system MUST provide real-time visibility into product stock.
    REQ-F-001, REQ-F-003, REQ-F-008
    """
    response = client.get("/api/v1/products/prod-tint-01")
    assert response.status_code == 200
    data = response.json()

    assert "available_stock" in data
    assert "stock_status" in data
    assert "in_stock" in data
    assert data["in_stock"] is True
    assert data["available_stock"] > 0
    assert data["stock_status"] in ["IN_STOCK", "LOW_STOCK", "OUT_OF_STOCK"]
    assert "inventory" in data
    assert data["inventory"]["available"] == data["available_stock"]


def test_inventory_sku_stock_query(client):
    """
    REQ-F-001, REQ-F-006: Dedicated SKU stock status endpoint.
    """
    response = client.get("/api/v1/inventory/SKU-TINT-100")
    assert response.status_code == 200
    data = response.json()

    assert data["sku"] == "SKU-TINT-100"
    assert data["available_stock"] >= 0
    assert data["status"] in ["IN_STOCK", "LOW_STOCK", "OUT_OF_STOCK"]


def test_inventory_service_direct_methods():
    """
    REQ-F-005, REQ-F-006: Dedicated Inventory Service methods get_product_stock, reserve_stock, release_stock.
    """
    sku = "SKU-CLEANSE-01"
    initial_stock = InventoryService.get_product_stock(sku)
    assert initial_stock.available_stock > 0

    initial_avail = initial_stock.available_stock

    # Reserve 5 items
    res = InventoryService.reserve_stock(sku=sku, quantity=5, session_id="test_sess_001")
    assert res.reservation_id.startswith("res_")
    assert res.quantity == 5
    assert res.status == "RESERVED"

    # Verify stock decremented
    after_res = InventoryService.get_product_stock(sku)
    assert after_res.available_stock == initial_avail - 5

    # Release reservation
    rel = InventoryService.release_stock(res.reservation_id)
    assert rel.status == "RELEASED"
    assert rel.quantity_released == 5

    # Verify stock restored
    after_rel = InventoryService.get_product_stock(sku)
    assert after_rel.available_stock == initial_avail


def test_reservation_exceeding_stock_rejected_with_http_400(client):
    """
    AC: The system MUST prevent users from adding a quantity greater than the available stock to their cart.
    REQ-F-002, REQ-F-004, REQ-F-015: Reject reservation with HTTP 400 when quantity > available stock.
    """
    sku = "SKU-TINT-400"
    stock_info = InventoryService.get_product_stock(sku)
    excess_quantity = stock_info.available_stock + 100

    payload = {
        "sku": sku,
        "quantity": excess_quantity,
        "session_id": "test_oversell_attempt"
    }

    response = client.post("/api/v1/inventory/reserve", json=payload)
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]


def test_release_inventory_endpoint(client):
    """
    REQ-F-006: Endpoint to release inventory.
    """
    sku = "SKU-SERUM-01"
    reserve_resp = client.post("/api/v1/inventory/reserve", json={
        "sku": sku,
        "quantity": 2,
        "session_id": "sess_release_test"
    })
    assert reserve_resp.status_code == 201
    res_id = reserve_resp.json()["reservation_id"]

    release_resp = client.post("/api/v1/inventory/release", json={"reservation_id": res_id})
    assert release_resp.status_code == 200
    assert release_resp.json()["status"] == "RELEASED"
    assert release_resp.json()["quantity_released"] == 2


def test_concurrent_reservations_prevent_overselling():
    """
    REQ-F-014, REQ-N-001, REQ-N-006: Multi-client reservation race tests to eliminate overselling.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    test_sku = "SKU-CONCURRENT-TEST"
    cursor.execute("""
        INSERT OR REPLACE INTO inventory (sku, product_id, available_stock, reserved_stock)
        VALUES (?, 'prod-tint-01', 10, 0)
    """, (test_sku,))
    conn.commit()
    conn.close()

    def attempt_reservation(client_id):
        try:
            return InventoryService.reserve_stock(
                sku=test_sku,
                quantity=1,
                session_id=f"sess_client_{client_id}"
            )
        except ValueError:
            return None

    # Spawn 20 concurrent attempts for 10 available items
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(attempt_reservation, range(20)))

    successful_reservations = [r for r in results if r is not None]
    assert len(successful_reservations) == 10, f"Expected exactly 10 successes, got {len(successful_reservations)}"

    # Check database state
    final_stock = InventoryService.get_product_stock(test_sku)
    assert final_stock.available_stock == 0
    assert final_stock.reserved_stock == 10
    assert final_stock.status == "OUT_OF_STOCK"
    assert final_stock.in_stock is False


def test_product_detail_page_html_elements_present():
    """
    AC: The UI MUST display the stock status on the product detail page and dynamically limit quantity selector.
    REQ-F-008, REQ-F-009
    """
    with open("public/pages/product-detail.html", "r", encoding="utf-8") as f:
        html = f.read()

    assert 'id="stock-status-badge"' in html
    assert 'id="quantity-input"' in html
    assert 'id="quantity-minus"' in html
    assert 'id="quantity-plus"' in html
    assert 'id="reserve-btn"' in html
    assert 'class="stock-status' in html
