# tests/test_wiring.py
"""Test Static Cross-Tier Wiring, Script Tags, and Client API Integrity."""

from pathlib import Path


def test_client_api_script_present_in_pages():
    """Verify that all public HTML pages include client API script tags."""
    public_dir = Path(__file__).resolve().parent.parent / "public" / "pages"
    html_files = list(public_dir.glob("*.html"))
    assert len(
        html_files) >= 9, f"Found {len(html_files)} HTML pages, expected >= 9"

    for html_p in html_files:
        content = html_p.read_text(encoding="utf-8")
        assert "/js/api.js" in content or "api.js" in content, f"Missing api.js in {html_p.name}"


def test_api_js_declares_endpoints():
    """Verify that public/js/api.js defines key REST methods."""
    api_js = Path(__file__).resolve().parent.parent / \
        "public" / "js" / "api.js"
    assert api_js.exists(), "public/js/api.js not found"
    content = api_js.read_text(encoding="utf-8")

    expected_methods = [
        "getProducts",
        "getProductDetail",
        "getHeroPromotions",
        "applyPromo",
        "reserveInventory",
        "processCheckout",
        "getOrder",
        "submitReturn",
        "erasePII"
    ]
    for m in expected_methods:
        assert m in content, f"api.js missing method {m}"
