# tests/test_e2e.py
"""End-to-End full user journey smoke test across entire cosmetic commerce lifecycle."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_full_user_purchase_and_return_lifecycle():
    """Verify complete end-to-end journey: Search -> PDP -> Reserve -> Checkout -> Track -> Return."""
    # 1. Search products
    search_res = client.get(
        "/api/v1/products?category=Foundation&skin_tone=Fair")
    assert search_res.status_code == 200
    products = search_res.json()["items"]
    assert len(products) > 0
    product = products[0]

    # 2. Get product details & shades
    pdp_res = client.get(f"/api/v1/products/{product['id']}")
    assert pdp_res.status_code == 200
    pdp = pdp_res.json()
    assert len(pdp["variants"]) > 0
    variant = pdp["variants"][0]

    # 3. Reserve inventory
    reserve_res = client.post("/api/v1/checkout/reserve", json={
        "items": [{"sku": variant["sku"], "quantity": 1}]
    })
    assert reserve_res.status_code == 200
    res_data = reserve_res.json()
    reservation_id = res_data["reservation_id"]

    # 4. Apply promo code
    promo_res = client.post("/api/v1/promotions/apply", json={
        "code": "GLOW10",
        "cart_total": pdp["price"]
    })
    assert promo_res.status_code == 200
    _ = promo_res.json()["discount_amount"]

    # 5. Process single-page checkout
    checkout_res = client.post("/api/v1/checkout/process", json={
        "reservation_id": reservation_id,
        "is_guest": True,
        "customer_email": "e2e.buyer@example.com",
        "customer_name": "E2E Buyer",
        "shipping_address": {
            "name": "E2E Buyer",
            "street": "123 Beauty Lane",
            "city": "Los Angeles",
            "state": "CA",
            "zip": "90001",
            "country": "USA"
        },
        "payment_method": "Apple Pay",
        "promo_code": "GLOW10",
        "items": [
            {
                "sku": variant["sku"],
                "product_id": pdp["id"],
                "product_name": pdp["name"],
                "shade_name": variant["shade_name"],
                "quantity": 1,
                "unit_price": pdp["price"]
            }
        ]
    })
    assert checkout_res.status_code == 201
    order_data = checkout_res.json()
    order_number = order_data["order_number"]
    _ = order_data["tracking_number"]

    # 6. Retrieve order tracking timeline
    order_res = client.get(f"/api/v1/orders/{order_number}")
    assert order_res.status_code == 200
    order_detail = order_res.json()
    assert order_detail["status"] == "confirmed"
    assert len(order_detail["tracking_events"]) > 0

    # 7. Customer shade exchange
    exchange_res = client.post("/api/v1/returns", json={
        "order_id": order_number,
        "return_type": "exchange",
        "original_sku": variant["sku"],
        "exchange_sku": "LS-20-WARM",
        "reason": "Need slightly warmer shade"
    })
    assert exchange_res.status_code == 201
    exchange_data = exchange_res.json()
    assert exchange_data["status"] == "approved"
    assert exchange_data["exchange_order_id"] is not None
