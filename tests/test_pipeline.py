"""
Automated Test Suite for Phase 3 — Unified Discovery Engine Pipeline Orchestration.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 7, 8, 10–13, 24, 28)
- part1_discovery_engine_architecture_final.md (Stages 2–6)

Verifies:
1. Raw natural language input reaches Stage 2 (Memory Interpretation).
2. Stage 2 V2 memory representation reaches Stage 3 (Signal Generation).
3. Stage 3 retrieval signals reach Stage 4 (Lexical Candidate Discovery & Coverage).
4. Stage 4 candidates reach Stage 5 (Compositional Multi-Clue Matching).
5. Stage 5 scored candidates reach Stage 6 (Contextual Result Organization).
6. Final pipeline output conforms strictly to the Section 18.2 DiscoveryResponse schema.
7. Pipeline operates strictly in RETRIEVAL_MODE="lexical_fts".
8. Zero embedding libraries (SentenceTransformer, torch, transformers) or model weights are loaded.
"""

import sys
import os
import asyncio
from pathlib import Path
from datetime import datetime, timezone
import pytest

# Ensure project root and backend are on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.config import settings
from app.representation.models import (
    V2MemoryRepresentation,
    ObjectConcept,
    PersonConcept,
    EventConcept,
    TemporalConcept,
)
from app.retrieval.models import (
    RetrievalFilter,
    DiscoveryResponse,
    CandidateResult,
    ScoreBreakdown,
)
from app.retrieval.pipeline import DiscoveryEnginePipeline


# =============================================================================
# 1. END-TO-END STAGE HANDOFF & CONNECTIVITY TESTS
# =============================================================================

def test_pipeline_raw_input_through_stages_2_to_6_flow():
    """
    Verifies that raw natural language input flows seamlessly through:
    Stage 1 (raw string) -> Stage 2 (V2 frame) -> Stage 3 (signals) ->
    Stage 4 (FTS retrieval) -> Stage 5 (compositional bonus) -> Stage 6 (ranking).
    """
    pipeline = DiscoveryEnginePipeline()
    raw_query = "rohtang ki ice wali photo"

    # Execute full pipeline end-to-end
    response = asyncio.run(pipeline.run(raw_query, top_k=5))

    # Stage 1 & 2 Verification: Raw input preserved and correctly parsed
    assert response.raw_input == raw_query
    assert isinstance(response.v2_frame, dict)
    assert response.v2_frame.get("spatial_setting") == "rohtang"
    objects = response.v2_frame.get("objects", [])
    assert any(o.get("name") == "ice" for o in objects)

    # Stage 3 Verification: Signals derived from V2 frame
    assert isinstance(response.retrieval_signals, dict)
    search_terms = response.retrieval_signals.get("search_query_terms", [])
    assert "ice" in search_terms
    assert "rohtang" in search_terms
    assert "ki" not in search_terms
    assert "wali" not in search_terms

    # Stage 4 & 5 Verification: Candidates retrieved and scored
    assert response.candidate_pool_size > 0
    assert len(response.results) > 0
    top_candidate = response.results[0]
    assert isinstance(top_candidate, CandidateResult)
    assert top_candidate.score > 0.0
    assert isinstance(top_candidate.score_breakdown, ScoreBreakdown)

    # Stage 6 Verification: Candidates organized and ranked 1-indexed
    for idx, cand in enumerate(response.results):
        assert cand.rank == idx + 1
        if idx > 0:
            assert response.results[idx - 1].score >= cand.score


def test_pipeline_kinship_and_cardinality_flow():
    """
    Verifies canonical Case 1: '5 sisters' flows through Stage 2 kinship interpretation
    and reaches candidate discovery.
    """
    pipeline = DiscoveryEnginePipeline()
    raw_query = "5 sisters"

    response = asyncio.run(pipeline.run(raw_query, top_k=5))

    # Stage 2 verification
    people = response.v2_frame.get("people", [])
    assert len(people) == 1
    assert people[0].get("role") == "sister"
    assert people[0].get("count") == 5

    # Conforms to response contract
    assert isinstance(response, DiscoveryResponse)
    assert response.raw_input == raw_query


def test_pipeline_compositional_bound_attribute_scoring():
    """
    Verifies Stage 5: bound attributes ('white' bound to 'motorcycle') receive
    the +1.5 compositional bonus when flowing through the pipeline.
    """
    pipeline = DiscoveryEnginePipeline()
    raw_query = "brother on white motorcycle"

    response = asyncio.run(pipeline.run(raw_query, top_k=5))

    assert response.candidate_pool_size > 0
    top = response.results[0]
    if "white" in top.content.lower() and "motorcycle" in top.content.lower():
        assert top.score_breakdown.bound_bonus == 1.5
        assert top.score >= 1.5


def test_pipeline_structured_and_temporal_filters():
    """
    Verifies structured filters (e.g. rating=1) and temporal bounds pass through
    pipeline.run() and constrain Stage 4 candidate discovery.
    """
    pipeline = DiscoveryEnginePipeline()
    raw_query = "google photos update search"
    filt = RetrievalFilter(
        rating=1,
        start_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2027, 1, 1, tzinfo=timezone.utc),
    )

    response = asyncio.run(pipeline.run(raw_query, filters=filt, top_k=5))

    assert response.candidate_pool_size > 0
    for cand in response.results:
        assert cand.metadata.get("rating") == 1


def test_pipeline_empty_query_deterministic_response():
    """Verifies that an empty raw input returns a deterministic zero-candidate response."""
    pipeline = DiscoveryEnginePipeline()
    response = asyncio.run(pipeline.run(""))

    assert isinstance(response, DiscoveryResponse)
    assert response.raw_input == ""
    assert response.candidate_pool_size == 0
    assert response.results == []
    assert "EMPTY_QUERY" in response.coverage_status


def test_pipeline_zero_model_isolation():
    """
    Verifies that the entire pipeline operates under RETRIEVAL_MODE='lexical_fts'
    without importing or loading SentenceTransformer, PyTorch, or model weights.
    """
    assert settings.RETRIEVAL_MODE == "lexical_fts"
    assert settings.embedding_selection_status == "lexical_fts_fallback"

    pipeline = DiscoveryEnginePipeline()
    assert pipeline is not None

    # Verify zero neural dependencies in sys.modules
    assert "sentence_transformers" not in sys.modules
    assert "torch" not in sys.modules
    assert "transformers" not in sys.modules


# =============================================================================
# 2. COMPOSITIONAL RETRIEVAL & BOUND ATTRIBUTE REGRESSION TESTS
# =============================================================================

def test_compositional_yellow_kurta_does_not_promote_yellow_truck():
    """
    Focused Regression Gate:
    Verifies that for 'yellow kurta':
    1. V2 frame binds 'yellow' attribute to 'kurta' object entity.
    2. Retrieval signals derive bound_attributes = [{'entity': 'kurta', 'attribute': 'yellow'}].
    3. Candidates matching only 'yellow' with an incompatible entity (e.g. 'yellow truck')
       are NOT incorrectly promoted as relevant results in the final results pool.
    """
    pipeline = DiscoveryEnginePipeline()
    response = asyncio.run(pipeline.run("yellow kurta", top_k=10))

    # Stage 2: Binding detection
    assert isinstance(response.v2_frame, dict)
    objects = response.v2_frame.get("objects", [])
    assert len(objects) == 1
    assert objects[0]["name"] == "kurta"
    assert "yellow" in objects[0]["attributes"]

    # Stage 3: Retrieval signals
    signals = response.retrieval_signals
    assert "kurta" in signals["visual_entities"]
    assert any(
        b["entity"] == "kurta" and b["attribute"] == "yellow"
        for b in signals.get("bound_attributes", [])
    )

    # Stage 4/5/6: Yellow truck or yellow-only incompatible distractors must NOT be promoted
    for result in response.results:
        content_lower = result.content.lower()
        # No truck chunk should ever be promoted for a kurta query
        assert "truck" not in content_lower, f"Incompatible 'truck' candidate was promoted: {result.content}"
        # If candidate does not contain kurta, it must not be promoted
        assert "kurta" in content_lower, f"Candidate lacking 'kurta' entity was promoted: {result.content}"


def test_compositional_analogous_queries_car_and_shirt():
    """
    Focused Regression Gate:
    Verifies analogous compositional queries:
    - 'red car': preserves 'car' entity constraint, binds 'red', retrieves car candidates
    - 'blue shirt': preserves 'shirt' entity constraint, binds 'blue'
    """
    pipeline = DiscoveryEnginePipeline()

    # 1. Analogous Query: 'red car'
    resp_car = asyncio.run(pipeline.run("red car", top_k=5))
    car_objs = resp_car.v2_frame.get("objects", [])
    assert any(o["name"] == "car" and "red" in o["attributes"] for o in car_objs)
    assert any(b["entity"] == "car" and b["attribute"] == "red" for b in resp_car.retrieval_signals.get("bound_attributes", []))
    # Must retrieve car candidates without promoting red non-car distractors
    for cand in resp_car.results:
        cand_lower = cand.content.lower()
        assert "car" in cand_lower or "automobile" in cand_lower

    # 2. Analogous Query: 'blue shirt'
    resp_shirt = asyncio.run(pipeline.run("blue shirt", top_k=5))
    shirt_objs = resp_shirt.v2_frame.get("objects", [])
    assert any(o["name"] == "shirt" and "blue" in o["attributes"] for o in shirt_objs)
    assert any(b["entity"] == "shirt" and b["attribute"] == "blue" for b in resp_shirt.retrieval_signals.get("bound_attributes", []))
    for cand in resp_shirt.results:
        assert "shirt" in cand.content.lower()


def test_distractor_penalty_demotes_attribute_only_mismatches():
    """
    Unit Verification of Stage 5 Distractor Penalty:
    When a candidate matches only the attribute ('yellow') of a bound pair
    without the required entity ('kurta'), it must receive a distractor penalty
    and be ranked strictly below entity-matching candidates.
    """
    from app.retrieval.signals import RetrievalSignals
    from app.retrieval.retriever import MultiPathRetriever

    retriever = MultiPathRetriever()
    signals = RetrievalSignals(
        visual_entities=["kurta"],
        bound_attributes=[{"entity": "kurta", "attribute": "yellow"}],
        search_query_terms=["kurta", "yellow"],
    )

    mock_rows = [
        {
            "chunk_id": "chunk_truck_1",
            "evidence_case_id": "case_truck",
            "content": "Found a yellow truck abandoned near the highway.",
            "raw_text": "yellow truck photo",
        },
        {
            "chunk_id": "chunk_kurta_1",
            "evidence_case_id": "case_kurta",
            "content": "Traditional Indian wedding with yellow kurta ceremony.",
            "raw_text": "yellow kurta photo",
        },
    ]

    scored = retriever._score_candidates(mock_rows, signals)
    assert len(scored) == 2

    kurta_cand = next(c for c in scored if c.candidate_id == "chunk_kurta_1")
    truck_cand = next(c for c in scored if c.candidate_id == "chunk_truck_1")

    # Kurta candidate receives bound bonus (+1.5) and 0 distractor penalty
    assert kurta_cand.score_breakdown.bound_bonus == 1.5
    assert kurta_cand.score_breakdown.distractor_penalty == 0.0

    # Truck candidate receives 0 bound bonus and 1.0 distractor penalty
    assert truck_cand.score_breakdown.bound_bonus == 0.0
    assert truck_cand.score_breakdown.distractor_penalty == 1.0

    # Kurta candidate is ranked strictly higher
    assert scored[0].candidate_id == "chunk_kurta_1"
    assert kurta_cand.score > truck_cand.score

