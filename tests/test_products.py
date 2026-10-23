# tests/test_products.py
"""Test Faceted Product Discovery, Shade Queries, and MoCRA / EU disclosures (REQ-F-001, REQ-F-011)."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_products_all():
    """Verify general product listing endpoint."""
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "facets" in data
    assert data["total"] >= 5


def test_faceted_search_skin_tone_and_finish():
    """Verify faceted filtering by skin tone and finish (REQ-F-001)."""
    response = client.get("/api/v1/products?skin_tone=Fair&finish=Radiant")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    for item in data["items"]:
        assert item["finish"] == "Radiant"
        assert "Fair" in item["skin_tones"]


def test_faceted_search_formulation_vegan():
    """Verify filtering by formulation flags (REQ-F-001)."""
    response = client.get("/api/v1/products?formulation=vegan")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    for item in data["items"]:
        assert "vegan" in item["formulations"]


def test_product_detail_mocra_and_eu_disclosures():
    """Verify FDA MoCRA and EU 1223/2009 disclosures on PDP (REQ-F-011)."""
    response = client.get("/api/v1/products/prod-lum-silk")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "prod-lum-silk"
    assert len(data["variants"]) >= 5
    assert len(data["ingredients"]) > 0
    assert "mocra_disclosures" in data
    assert data["mocra_disclosures"]["fda_facility_registration"] == "FEI-301829104"
    assert "eu_compliance" in data
    assert data["eu_compliance"]["cosing_registered"] is True


def test_product_detail_not_found():
    """Verify RFC-7807 404 response for non-existent product."""
    response = client.get("/api/v1/products/non-existent-id")
    assert response.status_code == 404
    data = response.json()
    assert data["title"] == "Product Not Found"
    assert data["status"] == 404
