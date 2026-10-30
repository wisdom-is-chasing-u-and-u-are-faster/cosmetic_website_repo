"""
API Endpoint Integration Tests
Tests /health, /api/v1/skin-profiles/options, /api/v1/products, and static view mounts.
Satisfies [ARCH-6311-AC1], [ARCH-6311-AC2]
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_health_probe():
    """Verify health endpoint returns status 200 OK and service metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "skincare-product-finder"


def test_skin_profile_options_endpoint():
    """[ARCH-6311-AC1] Users can fetch skin types and concerns for the quiz."""
    response = client.get("/api/v1/skin-profiles/options")
    assert response.status_code == 200
    data = response.json()
    assert "skin_types" in data
    assert "concerns" in data
    assert len(data["skin_types"]) >= 5
    assert any(st["id"] == "oily" for st in data["skin_types"])
    assert any(c["id"] == "acne" for c in data["concerns"])


def test_product_catalog_faceted_search():
    """[ARCH-6311-AC2] Catalog supports filtering by category, skin type, and concern."""
    # List all
    res = client.get("/api/v1/products")
    assert res.status_code == 200
    catalog = res.json()
    assert len(catalog["products"]) > 0
    assert "facets" in catalog

    # Filter by category cleansers
    res_cat = client.get("/api/v1/products?category=cleansers")
    assert res_cat.status_code == 200
    data_cat = res_cat.json()
    assert all(p["category"] == "cleansers" for p in data_cat["products"])

    # Filter by skin_type oily
    res_skin = client.get("/api/v1/products?skin_type=oily")
    assert res_skin.status_code == 200
    data_skin = res_skin.json()
    assert all("oily" in p["suitable_for"] for p in data_skin["products"])


def test_static_storefront_mounts():
    """Verify static html pages are mounted and served without 404."""
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "AURA SKINCARE" in res_index.text

    res_finder = client.get("/pages/product-finder.html")
    assert res_finder.status_code == 200
    assert "Skin Finder" in res_finder.text
