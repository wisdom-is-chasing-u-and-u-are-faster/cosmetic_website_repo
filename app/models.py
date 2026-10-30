"""
Data Models & Pydantic Schemas for Personalized Skincare Engine
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ------------------------------------------------------------------------------
# Skin Profiles & Quiz
# ------------------------------------------------------------------------------
class SkinTypeOption(BaseModel):
    id: str
    label: str
    description: str


class SkinConcernOption(BaseModel):
    id: str
    label: str
    icon: str
    description: Optional[str] = None


class SkinProfileOptionsResponse(BaseModel):
    skin_types: List[SkinTypeOption]
    concerns: List[SkinConcernOption]
    sensitivities: List[str]
    undertones: List[str]


class RecommendationRequest(BaseModel):
    skin_type: str = Field(..., description="Target skin type: oily, dry, combination, sensitive, normal")
    concerns: List[str] = Field(default_factory=list,
                                description="List of primary concerns: acne, aging, redness, etc.")
    sensitivity: str = Field(default="medium", description="Skin sensitivity level: low, medium, high")
    preferred_routine_depth: Optional[str] = "complete"
    budget_tier: Optional[str] = "all"


class RoutineStep(BaseModel):
    step_number: int
    step_name: str
    product_id: str
    product_slug: str
    product_name: str
    match_score: int
    match_reasons: List[str]
    price: float
    image_url: str
    routine_step: str


class RecommendationResponse(BaseModel):
    profile_summary: Dict[str, Any]
    routine_steps: List[RoutineStep]
    matched_products_count: int
    latency_ms: float


# ------------------------------------------------------------------------------
# Products & Shade Swatch Matrix
# ------------------------------------------------------------------------------
class ShadeSwatch(BaseModel):
    shade_id: str
    shade_name: str
    hex_color: str
    undertone: str
    sku: str
    in_stock: bool
    stock_quantity: int
    image_url: Optional[str] = None


class ProductSummary(BaseModel):
    id: str
    slug: str
    name: str
    category: str
    price: float
    rating: float
    review_count: int
    suitable_for: List[str]
    targets: List[str]
    image_url: str
    has_shade_swatches: bool
    in_stock: bool
    stock_quantity: int


class FacetItem(BaseModel):
    id: str
    name: str
    count: int


class ProductCatalogResponse(BaseModel):
    products: List[ProductSummary]
    facets: Dict[str, List[FacetItem]]
    pagination: Dict[str, int]


class ProductDetailResponse(BaseModel):
    id: str
    slug: str
    name: str
    category: str
    price: float
    rating: float
    reviews_count: int
    description: str
    inci_ingredients: str
    clinical_results: Optional[str] = None
    image_url: str
    routine_step: str
    suitable_skin_types: List[str]
    target_concerns: List[str]
    shade_swatches: List[ShadeSwatch]
    inventory: Dict[str, Any]


# ------------------------------------------------------------------------------
# Inventory Hold & Orders
# ------------------------------------------------------------------------------
class ReservationRequest(BaseModel):
    sku: str
    quantity: int = 1
    session_id: str


class ReservationResponse(BaseModel):
    reservation_id: str
    sku: str
    quantity: int
    expires_at: str
    ttl_seconds: int
    status: str


class CustomerAddress(BaseModel):
    street: str
    city: str
    state: str
    zip: str
    country: str = "US"


class CustomerInfo(BaseModel):
    email: str
    name: str
    shipping_address: CustomerAddress


class OrderItemRequest(BaseModel):
    sku: str
    product_id: str
    quantity: int = 1
    price: float


class OrderCreateRequest(BaseModel):
    reservation_id: Optional[str] = None
    items: List[OrderItemRequest]
    customer: CustomerInfo
    payment_method: str = "stripe"


class OrderCreateResponse(BaseModel):
    order_id: str
    status: str
    total_amount: float
    currency: str
    psp_routed: str
    transaction_id: str
    outbox_event_id: str
    created_at: str
