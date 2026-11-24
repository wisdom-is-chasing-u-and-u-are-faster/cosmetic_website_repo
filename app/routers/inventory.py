"""
Inventory Reservation & Stock Query Router (10-minute hold TTL)
Satisfies REQ-F-001, REQ-F-002, REQ-F-004, REQ-F-006, REQ-F-015
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from app.models import (
    ReservationRequest,
    ReservationResponse,
    ReleaseReservationRequest,
    ReleaseReservationResponse,
    StockStatusResponse,
)
from app.services.inventory_service import InventoryService

logger = logging.getLogger("inventory_router")
router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


@router.get("/{sku}", response_model=StockStatusResponse)
def get_inventory_stock(sku: str):
    """
    Retrieves real-time available stock and stock status for a SKU or product.
    Satisfies REQ-F-001 and REQ-F-006.
    """
    try:
        return InventoryService.get_product_stock(sku)
    except Exception as e:
        logger.error(f"Error fetching stock for SKU {sku}: {e}")
        raise HTTPException(status_code=500, detail="Internal error fetching stock status.")


@router.post("/reserve", response_model=ReservationResponse, status_code=201)
def reserve_inventory(req: ReservationRequest):
    """
    Creates an atomic inventory hold reservation with a 10-minute TTL to guarantee zero overselling.
    Returns HTTP 400 if requested quantity exceeds available stock (REQ-F-002, REQ-F-004, REQ-F-015).
    """
    try:
        return InventoryService.reserve_stock(
            sku=req.sku,
            quantity=req.quantity,
            session_id=req.session_id
        )
    except ValueError as e:
        logger.warning(f"Reservation rejected: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected reservation error: {e}")
        raise HTTPException(status_code=500, detail="Error processing inventory reservation.")


@router.post("/release", response_model=ReleaseReservationResponse, status_code=200)
def release_inventory(req: ReleaseReservationRequest):
    """
    Releases an existing reservation back into available stock.
    Satisfies REQ-F-006.
    """
    try:
        return InventoryService.release_stock(req.reservation_id)
    except ValueError as e:
        logger.warning(f"Release failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected release error: {e}")
        raise HTTPException(status_code=500, detail="Error releasing inventory reservation.")
