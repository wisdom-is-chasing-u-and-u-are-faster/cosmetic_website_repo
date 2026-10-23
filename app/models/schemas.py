# app/models/schemas.py
"""Pydantic data models for API requests and responses."""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# --- Product Models ---


class ShadeVariant(BaseModel):
    sku: str
    shade_name: str
    hex_code: str
    skin_tone: str
    undertone: str
    stock_quantity: int


class ProductListItem(BaseModel):
    id: str
    name: str
    brand: str
    category: str
    price: float
    rating: float
    description: Optional[str] = None
    finish: Optional[str] = None
    is_hero: bool = False
    shades: List[str] = []
    undertones: List[str] = []
    skin_tones: List[str] = []
    formulations: List[str] = []
    allergens: List[str] = []


class ProductDetailResponse(BaseModel):
    id: str
    name: str
    brand: str
    category: str
    price: float
    rating: float
    description: str
    finish: Optional[str] = None
    ingredients: List[str] = []
    formulations: List[str] = []
    allergens: List[str] = []
    mocra_disclosures: Dict[str, Any] = {}
    eu_compliance: Dict[str, Any] = {}
    variants: List[ShadeVariant] = []


class ProductSearchResponse(BaseModel):
    items: List[ProductListItem]
    total: int
    facets: Dict[str, List[str]]

# --- Promotion Models ---


class PromotionItem(BaseModel):
    sku: Optional[str] = None
    product_id: Optional[str] = None
    price: float
    quantity: int = 1


class PromoValidateRequest(BaseModel):
    code: str
    cart_total: float
    items: Optional[List[Dict[str, Any]]] = None


class PromoValidateResponse(BaseModel):
    valid: bool
    code: str
    discount_type: str
    discount_amount: float
    final_total: float
    message: str


class HeroPromotionsResponse(BaseModel):
    hero_products: List[ProductListItem]
    active_promotions: List[Dict[str, Any]]
    shade_bundles: List[Dict[str, Any]]

# --- Inventory & Checkout Models ---


class ReservationItem(BaseModel):
    sku: str
    quantity: int


class InventoryReserveRequest(BaseModel):
    items: List[ReservationItem]
    reservation_ttl_seconds: int = 900  # 15 minutes


class InventoryReserveResponse(BaseModel):
    reservation_id: str
    status: str = "reserved"
    expires_at: str
    items_reserved: int


class AddressModel(BaseModel):
    name: str
    street: str
    city: str
    state: str
    zip: str
    country: str = "USA"


class CartItemPayload(BaseModel):
    sku: str
    product_id: str
    product_name: str
    shade_name: str
    quantity: int
    unit_price: float


class CheckoutProcessRequest(BaseModel):
    reservation_id: Optional[str] = None
    is_guest: bool = True
    customer_email: str
    customer_name: Optional[str] = "Valued Customer"
    shipping_address: AddressModel
    billing_address: Optional[AddressModel] = None
    payment_method: str = "Stripe"  # Stripe, Apple Pay, Google Pay
    payment_token: Optional[str] = "tok_mock_payment_token"
    promo_code: Optional[str] = None
    items: List[CartItemPayload]


class CheckoutProcessResponse(BaseModel):
    order_id: str
    order_number: str
    status: str = "confirmed"
    total_amount: float
    discount_amount: float = 0.0
    tracking_carrier: str = "FedEx Express"
    tracking_number: str
    estimated_delivery: str
    message: str = "Order placed successfully"

# --- Orders & Tracking Models ---


class TrackingEventModel(BaseModel):
    timestamp: str
    status: str
    location: str
    description: str


class OrderDetailResponse(BaseModel):
    id: str
    order_number: str
    customer_email: str
    is_guest: bool
    total_amount: float
    discount_amount: float
    promo_code: Optional[str]
    payment_method: str
    payment_status: str
    tracking_carrier: str
    tracking_number: str
    status: str
    shipping_address: Dict[str, Any]
    items: List[Dict[str, Any]]
    tracking_events: List[TrackingEventModel]
    created_at: str

# --- Returns & Exchange Models ---


class ReturnRequest(BaseModel):
    order_id: str
    return_type: str = "return"  # return or exchange
    original_sku: str
    exchange_sku: Optional[str] = None
    reason: str


class ReturnResponse(BaseModel):
    return_id: str
    order_id: str
    return_type: str
    status: str = "approved"
    return_label_url: str
    exchange_order_id: Optional[str] = None
    message: str

# --- Webhook & Logistics Models ---


class Webhook3PLPayload(BaseModel):
    event_type: str
    tracking_number: str
    order_id: Optional[str] = None
    status: str
    location: str
    timestamp: Optional[str] = None
    notes: Optional[str] = None


class WebhookResponse(BaseModel):
    received: bool = True
    event_id: str
    status: str = "processed"

# --- Account & GDPR PII Models ---


class CustomerAccountResponse(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    skin_tone_profile: Optional[str] = None
    undertone_profile: Optional[str] = None
    is_pii_erased: bool = False


class CustomerUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    skin_tone_profile: Optional[str] = None
    undertone_profile: Optional[str] = None


class PIIErasureResponse(BaseModel):
    customer_id: str
    status: str = "erased"
    anonymized_email: str
    message: str = "All Personally Identifiable Information has been permanently erased in compliance with GDPR/CCPA."
