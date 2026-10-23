# tests/test_db.py
"""Test Database Schema and Seed Data initialization (REQ-F-001, REQ-F-011)."""

from app.db.database import get_connection, init_database


def test_database_initialization():
    """Verify that all database tables and seeds are properly loaded."""
    init_database()
    conn = get_connection()
    cursor = conn.cursor()

    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [r[0] for r in cursor.fetchall()]
    expected_tables = [
        "products", "product_shades", "product_attributes",
        "promotions", "inventory_reservations", "customers",
        "orders", "order_items", "returns", "tracking_events",
        "idempotency_records", "audit_logs"
    ]
    for tbl in expected_tables:
        assert tbl in tables, f"Missing table: {tbl}"

    # Verify seeded products
    cursor.execute("SELECT COUNT(*) FROM products;")
    prod_count = cursor.fetchone()[0]
    assert prod_count >= 5

    # Verify seeded shades
    cursor.execute("SELECT COUNT(*) FROM product_shades;")
    shade_count = cursor.fetchone()[0]
    assert shade_count >= 10

    conn.close()
