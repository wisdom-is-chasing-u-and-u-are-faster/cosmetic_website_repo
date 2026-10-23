# app/api/promotions.py
"""Promotions engine and hero merchandising endpoints (REQ-F-005, REQ-F-015)."""

import json
import sqlite3
from fastapi import APIRouter, Depends
from app.db.database import get_db
from app.models.schemas import PromoValidateRequest, PromoValidateResponse, HeroPromotionsResponse, ProductListItem
from app.core.errors import AppException

router = APIRouter(prefix="/api/v1/promotions", tags=["Promotions"])


@router.get("/hero", response_model=HeroPromotionsResponse)
def get_hero_promotions(conn: sqlite3.Connection = Depends(get_db)):
    """Retrieve hero products, active promotions, and shade bundles (REQ-F-005)."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, pa.formulations, pa.allergens
        FROM products p
        LEFT JOIN product_attributes pa ON p.id = pa.product_id
        WHERE p.is_hero = 1
    """)
    rows = cursor.fetchall()

    hero_products = []
    for r in rows:
        hero_products.append(
            ProductListItem(
                id=r["id"],
                name=r["name"],
                brand=r["brand"],
                category=r["category"],
                price=float(r["price"]),
                rating=float(r["rating"]),
                description=r["description"],
                finish=r["finish"],
                is_hero=True,
                formulations=json.loads(
                    r["formulations"]) if r["formulations"] else [],
                allergens=json.loads(r["allergens"]) if r["allergens"] else []
            )
        )

    cursor.execute(
        "SELECT code, description, discount_type, discount_value, min_spend FROM promotions WHERE is_active = 1")
    promo_rows = cursor.fetchall()
    active_promos = [dict(p) for p in promo_rows]

    shade_bundles = [
        {
            "id": "bundle-radiant-glow",
            "title": "Radiant Complexion Trio",
            "description": "Luminous Silk Foundation + Hydra-Glow Concealer + Solar Bronzer",
            "bundle_price": 95.00,
            "original_price": 116.00,
            "savings": "$21.00 (18% Off)",
            "product_ids": ["prod-lum-silk", "prod-hydra-glow", "prod-solar-bronze"]
        },
        {
            "id": "bundle-velvet-lip-duo",
            "title": "Velvet Lip Duo",
            "description": "Rose Cashmere + Warm Caramel Nude",
            "bundle_price": 48.00,
            "original_price": 56.00,
            "savings": "$8.00 (14% Off)",
            "product_ids": ["prod-vel-matte"]
        }
    ]

    return HeroPromotionsResponse(
        hero_products=hero_products,
        active_promotions=active_promos,
        shade_bundles=shade_bundles
    )


@router.post("/apply", response_model=PromoValidateResponse)
def apply_promotion(payload: PromoValidateRequest,
                    conn: sqlite3.Connection = Depends(get_db)):
    """Validate promo code against current cart and calculate discounts (REQ-F-015)."""
    cursor = conn.cursor()
    code_clean = payload.code.strip().upper()
    cursor.execute(
        "SELECT * FROM promotions WHERE UPPER(code) = ? AND is_active = 1",
        (code_clean,
         ))
    promo = cursor.fetchone()

    if not promo:
        raise AppException(
            status_code=400,
            title="Invalid Promotional Code",
            detail=f"Promotion code '{payload.code}' is invalid or expired."
        )

    min_spend = float(promo["min_spend"])
    if payload.cart_total < min_spend:
        raise AppException(
            status_code=400,
            title="Minimum Spend Not Met",
            detail=f"Promotion code '{code_clean}' requires a minimum cart total of ${min_spend:.2f}."
        )

    discount_type = promo["discount_type"]
    discount_val = float(promo["discount_value"])
    if discount_type == "percentage":
        discount_amount = round(payload.cart_total * (discount_val / 100.0), 2)
    else:
        discount_amount = min(discount_val, payload.cart_total)

    final_total = max(0.0, round(payload.cart_total - discount_amount, 2))

    return PromoValidateResponse(
        valid=True,
        code=code_clean,
        discount_type=discount_type,
        discount_amount=discount_amount,
        final_total=final_total,
        message=f"Success! {promo['description']} applied."
    )
