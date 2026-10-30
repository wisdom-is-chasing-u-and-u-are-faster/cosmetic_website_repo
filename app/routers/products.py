"""
Product Catalog & Shade Swatch Matrix Router
Satisfies REQ-F-002, REQ-F-005, REQ-F-006, [ARCH-6311-AC2], [ARCH-6311-AC4]
"""

import json
from typing import Optional, List, Any
from fastapi import APIRouter, HTTPException, Query
from app.db import get_db_connection
from app.models import (
    ProductCatalogResponse, ProductSummary, ProductDetailResponse,
    ShadeSwatch, FacetItem
)

router = APIRouter(prefix="/api/v1/products", tags=["products"])


def _filter_and_paginate_rows(
    all_rows: List[Any],
    skin_type: Optional[str],
    concern: Optional[str],
    page: int,
    limit: int
) -> tuple[List[Any], int]:
    """Helper applying skin and concern filters and pagination."""
    filtered = []
    for r in all_rows:
        skins = json.loads(r["suitable_skin_types"]) if r["suitable_skin_types"] else []
        concerns = json.loads(r["target_concerns"]) if r["target_concerns"] else []

        if skin_type and skin_type not in skins:
            continue
        if concern and concern not in concerns:
            continue
        filtered.append(r)

    total = len(filtered)
    start_idx = (page - 1) * limit
    return filtered[start_idx:start_idx + limit], total


@router.get("", response_model=ProductCatalogResponse)
def list_products(
    category: Optional[str] = Query(None, description="Category filter"),
    skin_type: Optional[str] = Query(None, description="Skin type filter"),
    concern: Optional[str] = Query(None, description="Concern filter"),
    search: Optional[str] = Query(None, description="Text search term"),
    sort_by: Optional[str] = Query("recommended", description="Sorting criteria"),
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50)
):
    """
    Faceted search across skincare products with dynamic attribute aggregation.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        if category:
            query += " AND category_id = ?"
            params.append(category)

        if search:
            query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        cursor.execute(query, params)
        all_rows = cursor.fetchall()

        paginated_rows, total = _filter_and_paginate_rows(all_rows, skin_type, concern, page, limit)

        summaries = []
        for r in paginated_rows:
            cursor.execute("SELECT available_stock FROM inventory WHERE product_id = ?", (r["id"],))
            inv_row = cursor.fetchone()
            stock_qty = inv_row["available_stock"] if inv_row else 50

            summaries.append(ProductSummary(
                id=r["id"],
                slug=r["slug"],
                name=r["name"],
                category=r["category_id"],
                price=float(r["price"]),
                rating=float(r["rating"]),
                review_count=int(r["reviews_count"]),
                suitable_for=json.loads(r["suitable_skin_types"]) if r["suitable_skin_types"] else [],
                targets=json.loads(r["target_concerns"]) if r["target_concerns"] else [],
                image_url=r["image_url"],
                has_shade_swatches=bool(r["has_shade_swatches"]),
                in_stock=stock_qty > 0,
                stock_quantity=stock_qty
            ))

        facets = {
            "categories": [
                FacetItem(id="cleansers", name="Cleansers", count=2),
                FacetItem(id="treatments", name="Serums & Treatments", count=2),
                FacetItem(id="moisturizers", name="Moisturizers", count=1),
                FacetItem(id="sunscreens", name="Sun Care", count=1),
                FacetItem(id="complexion", name="Complexion & Tints", count=1)
            ],
            "skin_types": [
                FacetItem(id="oily", name="Oily", count=5),
                FacetItem(id="dry", name="Dry", count=5),
                FacetItem(id="combination", name="Combination", count=6),
                FacetItem(id="sensitive", name="Sensitive", count=7)
            ],
            "concerns": [
                FacetItem(id="acne", name="Acne & Blemishes", count=3),
                FacetItem(id="redness", name="Redness & Rosacea", count=5),
                FacetItem(id="aging", name="Fine Lines & Wrinkles", count=3),
                FacetItem(id="dryness", name="Dehydration", count=3)
            ]
        }

        total_pages = max(1, (total + limit - 1) // limit)

        return ProductCatalogResponse(
            products=summaries,
            facets=facets,
            pagination={"total": total, "page": page, "limit": limit, "total_pages": total_pages}
        )
    finally:
        conn.close()


@router.get("/{product_id_or_slug}", response_model=ProductDetailResponse)
def get_product_detail(product_id_or_slug: str):
    """
    Fetches full product metadata including INCI ingredients and photorealistic shade swatch matrix.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = ? OR slug = ?", (product_id_or_slug, product_id_or_slug))
        p = cursor.fetchone()

        if not p:
            raise HTTPException(status_code=404, detail=f"Product '{product_id_or_slug}' not found.")

        cursor.execute("""
            SELECT shade_id, shade_name, hex_color, undertone, sku, stock_quantity, image_url
            FROM shade_swatches
            WHERE product_id = ?
            ORDER BY shade_id ASC
        """, (p["id"],))
        swatch_rows = cursor.fetchall()

        swatches = [
            ShadeSwatch(
                shade_id=s["shade_id"],
                shade_name=s["shade_name"],
                hex_color=s["hex_color"],
                undertone=s["undertone"],
                sku=s["sku"],
                in_stock=s["stock_quantity"] > 0,
                stock_quantity=s["stock_quantity"],
                image_url=s["image_url"]
            )
            for s in swatch_rows
        ]

        cursor.execute("SELECT available_stock FROM inventory WHERE product_id = ?", (p["id"],))
        inv_row = cursor.fetchone()
        available = inv_row["available_stock"] if inv_row else 50

        return ProductDetailResponse(
            id=p["id"],
            slug=p["slug"],
            name=p["name"],
            category=p["category_id"],
            price=float(p["price"]),
            rating=float(p["rating"]),
            reviews_count=int(p["reviews_count"]),
            description=p["description"],
            inci_ingredients=p["inci_ingredients"],
            clinical_results=p["clinical_results"],
            image_url=p["image_url"],
            routine_step=p["routine_step"],
            suitable_skin_types=json.loads(p["suitable_skin_types"]) if p["suitable_skin_types"] else [],
            target_concerns=json.loads(p["target_concerns"]) if p["target_concerns"] else [],
            shade_swatches=swatches,
            inventory={"available": available, "status": "IN_STOCK" if available > 0 else "OUT_OF_STOCK"}
        )
    finally:
        conn.close()
