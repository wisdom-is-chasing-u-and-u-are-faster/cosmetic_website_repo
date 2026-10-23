# tests/test_app.py
"""Test Application Assembly, Health Check Probe, and OpenAPI schema generation."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Verify system health and liveness probe."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "cosmetics-store-api"


def test_openapi_schema_generated():
    """Verify FastAPI OpenAPI documentation is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "paths" in data
    assert "/api/v1/products" in data["paths"]
    assert "/api/v1/checkout/process" in data["paths"]
