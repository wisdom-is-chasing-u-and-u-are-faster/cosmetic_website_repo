# app/api/products.py
"""Product discovery and catalog API endpoints with faceted search and MoCRA disclosures."""

import json
import sqlite3
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from app.db.database import get_db
from app.models.schemas import ProductSearchResponse, ProductListItem, ProductDetailResponse, ShadeVariant
from app.core.errors import AppException

router = APIRouter(prefix="/api/v1/products", tags=["Products"])


@router.get("", response_model=ProductSearchResponse)
def list_products(
    search: Optional[str] = Query(None, description="Free-text search query"),
    category: Optional[str] = Query(None, description="Product category"),
    skin_tone: Optional[str] = Query(None, description="Skin tone (Fair, Light, Medium, Tan, Deep)"),
    undertone: Optional[str] = Query(None, description="Undertone (Cool, Neutral, Warm, Olive)"),
    finish: Optional[str] = Query(None, description="Finish type (Matte, Dewy, Radiant, Satin)"),
    formulation: Optional[str] = Query(None, description="Formulation filter (vegan, cruelty-free, etc.)"),
    allergens: Optional[str] = Query(None, description="Allergen exclusion (fragrance-free, etc.)"),
    sort: Optional[str] = Query("popular", description="Sort by popular, price_asc, price_desc, rating"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    conn: sqlite3.Connection = Depends(get_db)
):
    """Faceted search and listing across cosmetic products and shade attributes (REQ-F-001)."""
    cursor = conn.cursor()

    query = """
        SELECT p.id, p.name, p.brand, p.category, p.price, p.rating, p.description, p.finish, p.is_hero,
               pa.formulations, pa.allergens
        FROM products p
        LEFT JOIN product_attributes pa ON p.id = pa.product_id
        WHERE 1=1
    """
    params = []

    if category and category.lower() != "all":
        query += " AND LOWER(p.category) = LOWER(?)"
        params.append(category)

    if finish and finish.lower() != "all":
        query += " AND LOWER(p.finish) = LOWER(?)"
        params.append(finish)

    if search:
        query += " AND (LOWER(p.name) LIKE ? OR LOWER(p.brand) LIKE ? OR LOWER(p.description) LIKE ?)"
        s_term = f"%{search.lower()}%"
        params.extend([s_term, s_term, s_term])

    cursor.execute(query, params)
    rows = cursor.fetchall()

    items: List[ProductListItem] = []
    all_skin_tones: set = set()
    all_undertones: set = set()
    all_finishes: set = set()
    all_formulations: set = set()
    all_allergens: set = set()

    for r in rows:
        pid = r["id"]
        # Fetch shades for this product
        s_cursor = conn.cursor()
        s_cursor.execute("SELECT shade_name, skin_tone, undertone FROM product_shades WHERE product_id = ?", (pid,))
        shades_data = s_cursor.fetchall()

        prod_shades = [s["shade_name"] for s in shades_data]
        prod_skin_tones = list(set(s["skin_tone"] for s in shades_data))
        prod_undertones = list(set(s["undertone"] for s in shades_data))

        prod_forms = json.loads(r["formulations"]) if r["formulations"] else []
        prod_allers = json.loads(r["allergens"]) if r["allergens"] else []

        # Filter by skin_tone facet
        if skin_tone and skin_tone.lower() != "all":
            if not any(st.lower() == skin_tone.lower() for st in prod_skin_tones):
                continue

        # Filter by undertone facet
        if undertone and undertone.lower() != "all":
            if not any(ut.lower() == undertone.lower() for ut in prod_undertones):
                continue

        # Filter by formulation facet
        if formulation and formulation.lower() != "all":
            if not any(f.lower() == formulation.lower() for f in prod_forms):
                continue

        # Filter by allergen-free facet
        if allergens and allergens.lower() != "all":
            if not any(a.lower() == allergens.lower() for a in prod_allers):
                continue

        all_skin_tones.update(prod_skin_tones)
        all_undertones.update(prod_undertones)
        if r["finish"]:
            all_finishes.add(r["finish"])
        all_formulations.update(prod_forms)
        all_allergens.update(prod_allers)

        items.append(
            ProductListItem(
                id=r["id"],
                name=r["name"],
                brand=r["brand"],
                category=r["category"],
                price=float(r["price"]),
                rating=float(r["rating"]),
                description=r["description"],
                finish=r["finish"],
                is_hero=bool(r["is_hero"]),
                shades=prod_shades,
                skin_tones=prod_skin_tones,
                undertones=prod_undertones,
                formulations=prod_forms,
                allergens=prod_allers
            )
        )

    # Sorting
    if sort == "price_asc":
        items.sort(key=lambda x: x.price)
    elif sort == "price_desc":
        items.sort(key=lambda x: x.price, reverse=True)
    elif sort == "rating":
        items.sort(key=lambda x: x.rating, reverse=True)

    # Pagination
    total = len(items)
    start = (page - 1) * limit
    paged_items = items[start:start + limit]

    facets = {
        "skin_tones": sorted(list(all_skin_tones)),
        "undertones": sorted(list(all_undertones)),
        "finishes": sorted(list(all_finishes)),
        "formulations": sorted(list(all_formulations)),
        "allergens": sorted(list(all_allergens))
    }

    return ProductSearchResponse(items=paged_items, total=total, facets=facets)


@router.get("/{product_id}", response_model=ProductDetailResponse)
def get_product_detail(product_id: str, conn: sqlite3.Connection = Depends(get_db)):
    """Fetch product specifications, shades, ingredients, and MoCRA / EU disclosures (REQ-F-011)."""
    lookup_id = product_id
    if product_id in ["{id}", "{product_id}"]:
        lookup_id = "prod-lum-silk"

    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, pa.formulations, pa.allergens, pa.ingredients, pa.mocra_disclosures, pa.eu_compliance
        FROM products p
        LEFT JOIN product_attributes pa ON p.id = pa.product_id
        WHERE p.id = ?
    """, (lookup_id,))
    row = cursor.fetchone()

    if not row:
        raise AppException(
            status_code=404,
            title="Product Not Found",
            detail=f"Cosmetic product with ID '{product_id}' was not found in catalog."
        )

    # Fetch shade variants
    cursor.execute("SELECT * FROM product_shades WHERE product_id = ?", (row["id"],))
    shade_rows = cursor.fetchall()

    variants = [
        ShadeVariant(
            sku=s["sku"],
            shade_name=s["shade_name"],
            hex_code=s["hex_code"],
            skin_tone=s["skin_tone"],
            undertone=s["undertone"],
            stock_quantity=s["stock_quantity"]
        ) for s in shade_rows
    ]

    ingredients_raw = row["ingredients"] or ""
    ingredients_list = [i.strip() for i in ingredients_raw.split(",") if i.strip()]

    formulations = json.loads(row["formulations"]) if row["formulations"] else []
    allergens = json.loads(row["allergens"]) if row["allergens"] else []
    mocra = json.loads(row["mocra_disclosures"]) if row["mocra_disclosures"] else {}
    eu = json.loads(row["eu_compliance"]) if row["eu_compliance"] else {}

    return ProductDetailResponse(
        id=row["id"],
        name=row["name"],
        brand=row["brand"],
        category=row["category"],
        price=float(row["price"]),
        rating=float(row["rating"]),
        description=row["description"] or "",
        finish=row["finish"],
        ingredients=ingredients_list,
        formulations=formulations,
        allergens=allergens,
        mocra_disclosures=mocra,
        eu_compliance=eu,
        variants=variants
    )
