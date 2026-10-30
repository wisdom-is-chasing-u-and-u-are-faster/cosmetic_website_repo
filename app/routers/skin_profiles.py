"""
Skin Profiles & Quiz Options Router
Satisfies REQ-F-001, [ARCH-6311-AC1]
"""

from fastapi import APIRouter
from app.db import get_db_connection
from app.models import SkinProfileOptionsResponse, SkinTypeOption, SkinConcernOption

router = APIRouter(prefix="/api/v1/skin-profiles", tags=["skin-profiles"])


@router.get("/options", response_model=SkinProfileOptionsResponse)
def get_skin_profile_options():
    """
    Returns available skin types, primary skin concerns, sensitivity levels, and undertones
    for the interactive skincare quiz and recommendation filters.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        cursor.execute("SELECT id, label, description FROM skin_types ORDER BY rowid ASC")
        skin_types = [SkinTypeOption(id=r["id"], label=r["label"], description=r["description"])
                      for r in cursor.fetchall()]

        cursor.execute("SELECT id, label, icon, description FROM skin_concerns ORDER BY rowid ASC")
        concerns = [
            SkinConcernOption(
                id=r["id"],
                label=r["label"],
                icon=r["icon"],
                description=r["description"]) for r in cursor.fetchall()]

        sensitivities = ["low", "medium", "high"]
        undertones = ["cool", "warm", "neutral", "olive"]

        return SkinProfileOptionsResponse(
            skin_types=skin_types,
            concerns=concerns,
            sensitivities=sensitivities,
            undertones=undertones
        )
    finally:
        conn.close()
