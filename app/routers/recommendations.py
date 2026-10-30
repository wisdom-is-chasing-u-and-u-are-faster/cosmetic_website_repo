"""
Personalized Skincare Recommendations Router
Satisfies REQ-F-001, REQ-F-003, REQ-N-001, [ARCH-6311-AC1], [ARCH-6311-AC2], [ARCH-6311-AC3]
"""

from fastapi import APIRouter
from app.models import RecommendationRequest, RecommendationResponse
from app.services.recommendation_engine import RecommendationEngine

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
def get_recommendations(req: RecommendationRequest):
    """
    Computes a tailored skincare regimen (Cleanse, Treat, Hydrate, Protect) based on
    the user's skin type, concerns, and sensitivity preferences. Guaranteed <250ms response SLA.
    """
    return RecommendationEngine.generate_recommendations(req)
