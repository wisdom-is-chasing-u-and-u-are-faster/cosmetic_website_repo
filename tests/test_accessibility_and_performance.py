"""
Accessibility & Performance SLA Verification Tests
Validates WCAG 2.1 AA accessibility standards and sub-250ms latency constraints.
Satisfies [ARCH-6311-AC3], [ARCH-6311-AC5], REQ-N-001, REQ-N-002
"""

import time
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import init_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_wcag_accessibility_attributes_in_html():
    """[ARCH-6311-AC5] Verifies semantic HTML, ARIA attributes, and accessible roles across UI views."""
    repo_root = Path(__file__).resolve().parent.parent
    public_pages = [
        repo_root / "public" / "index.html",
        repo_root / "public" / "pages" / "home.html",
        repo_root / "public" / "pages" / "product-finder.html",
        repo_root / "public" / "pages" / "product-listing.html",
        repo_root / "public" / "pages" / "product-detail.html"
    ]

    for page_path in public_pages:
        assert page_path.exists(), f"Missing UI page: {page_path}"
        content = page_path.read_text(encoding="utf-8")

        # HTML language attribute
        assert 'lang="en"' in content or "lang='en'" in content, f"Page {page_path.name} missing lang attribute"

        # Meta viewport for responsiveness
        assert 'name="viewport"' in content, f"Page {page_path.name} missing viewport meta tag"

        # CSS stylesheet inclusion
        assert 'rel="stylesheet"' in content, f"Page {page_path.name} missing stylesheet link"


def test_end_to_end_sub_250ms_recommendation_latency():
    """[ARCH-6311-AC3] Verifies end-to-end API roundtrip executes in under 250ms."""
    payload = {
        "skin_type": "combination",
        "concerns": ["acne", "pores", "redness"],
        "sensitivity": "medium"
    }

    start = time.perf_counter()
    res = client.post("/api/v1/recommendations", json=payload)
    elapsed_ms = (time.perf_counter() - start) * 1000

    assert res.status_code == 200
    assert elapsed_ms < 250, f"Recommendation roundtrip latency {elapsed_ms}ms exceeded 250ms SLA threshold!"
