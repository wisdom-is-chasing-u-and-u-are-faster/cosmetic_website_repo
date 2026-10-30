"""
Inventory Reservation Router (10-minute hold TTL)
Satisfies REQ-F-007, REQ-F-009
"""

from fastapi import APIRouter, HTTPException
from app.models import ReservationRequest, ReservationResponse
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/api/v1/inventory", tags=["inventory"])


@router.post("/reserve", response_model=ReservationResponse, status_code=201)
def reserve_inventory(req: ReservationRequest):
    """
    Creates an atomic inventory hold reservation with a 10-minute TTL to guarantee zero overselling.
    """
    try:
        return InventoryService.reserve_inventory(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
