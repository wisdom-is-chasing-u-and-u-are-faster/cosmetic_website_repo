"""
Orders & Checkout Router (Dual-PSP smart routing & Transactional Outbox)
Satisfies REQ-F-008, REQ-F-010
"""

from fastapi import APIRouter, HTTPException
from app.models import OrderCreateRequest, OrderCreateResponse
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post("", response_model=OrderCreateResponse, status_code=201)
def create_order(req: OrderCreateRequest):
    """
    Submits an order, routes payment via primary/secondary PSP, commits inventory hold,
    and logs outbox event for CDC pipeline.
    """
    try:
        return OrderService.create_order(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
