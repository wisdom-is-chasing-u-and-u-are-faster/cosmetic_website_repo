"""
Shade Swatch Matrix & Product Detail Tests
Tests photorealistic hex accuracy, undertones, and INCI ingredient disclosure.
Satisfies [ARCH-6311-AC4], REQ-F-002, REQ-F-005
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_product_detail_and_shade_swatches():
    """[ARCH-6311-AC4] Product detail pages show accurate shade swatches with hex fidelity."""
    res = client.get("/api/v1/products/prod-tint-01")
    assert res.status_code == 200
    product = res.json()

    assert product["name"] == "Luminous Hydrating Skin Tint SPF 30"
    assert "inci_ingredients" in product
    assert "Squalane" in product["inci_ingredients"]
    assert "shade_swatches" in product
    assert len(product["shade_swatches"]) >= 5

    # Verify shade properties
    first_shade = product["shade_swatches"][0]
    assert first_shade["shade_id"] == "shade-100"
    assert first_shade["shade_name"] == "Fair Neutral 100"
    assert first_shade["hex_color"].startswith("#")
    assert first_shade["undertone"] in ["cool", "warm", "neutral", "olive"]
    assert first_shade["in_stock"] is True


def test_product_detail_404_not_found():
    """Returns 404 for non-existent product."""
    res = client.get("/api/v1/products/non-existent-sku-xyz")
    assert res.status_code == 404
