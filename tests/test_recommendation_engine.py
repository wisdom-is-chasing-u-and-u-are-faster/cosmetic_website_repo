"""
Personalized Skincare Matching Engine Unit Tests
Tests multi-factor scoring, routine step generation, and execution latency (<250ms).
Satisfies [ARCH-6311-AC1], [ARCH-6311-AC2], [ARCH-6311-AC3]
"""

import time
import pytest
from app.models import RecommendationRequest
from app.services.recommendation_engine import RecommendationEngine
from app.db import init_database


@pytest.fixture(autouse=True)
def setup_db():
    init_database()


def test_personalized_recommendation_generation():
    """[ARCH-6311-AC1] [ARCH-6311-AC2] Generates customized 4-step routine based on skin profile."""
    req = RecommendationRequest(
        skin_type="combination",
        concerns=["acne", "redness"],
        sensitivity="medium"
    )

    result = RecommendationEngine.generate_recommendations(req)

    assert result.profile_summary["skin_type"] == "combination"
    assert "acne" in result.profile_summary["concerns"]
    assert len(result.routine_steps) == 4

    step_names = [s.routine_step for s in result.routine_steps]
    assert step_names == ["cleanse", "treat", "hydrate", "protect"]

    # Check match score calculation
    for step in result.routine_steps:
        assert step.match_score >= 70
        assert len(step.match_reasons) > 0


def test_recommendation_response_time_under_250ms():
    """[ARCH-6311-AC3] Product results must load in under 250ms SLA."""
    req = RecommendationRequest(
        skin_type="oily",
        concerns=["pores", "acne"],
        sensitivity="low"
    )

    start = time.perf_counter()
    result = RecommendationEngine.generate_recommendations(req)
    duration_ms = (time.perf_counter() - start) * 1000

    assert duration_ms < 250, f"Recommendation latency {duration_ms}ms exceeded 250ms SLA threshold!"
    assert result.latency_ms < 250
