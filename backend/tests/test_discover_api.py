"""
Automated Test Suite for Discovery Engine HTTP API.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 18.1, 18.2)
- part1_discovery_engine_architecture_final.md (Stages 2–6)

Verifies:
1. POST /api/v1/discover exists and does not return 404.
2. Valid canonical queries produce HTTP 200.
3. Response conforms strictly to Section 18.2 DiscoveryResponse schema.
4. top_k parameter is respected in candidate truncation.
5. Invalid input (empty payload, negative top_k, invalid types) produces appropriate 4xx responses.
6. Endpoint invokes the existing DiscoveryEnginePipeline rather than duplicating logic.
7. Structured V2 representations and filters are accepted and forwarded to the pipeline.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path and environment loaded
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.main import app
from app.api.v1.endpoints.discover import get_pipeline
from app.retrieval.pipeline import DiscoveryEnginePipeline
from app.retrieval.models import (
    DiscoveryResponse,
    CandidateResult,
    ScoreBreakdown,
    RetrievalFilter,
)
from app.representation.models import V2MemoryRepresentation, PersonConcept


@pytest.fixture(scope="module")
def api_client():
    """Module-scoped TestClient."""
    with TestClient(app) as test_client:
        yield test_client


# =============================================================================
# 1. ROUTE EXISTENCE & BASIC STATUS
# =============================================================================

def test_discover_endpoint_exists_not_404(api_client: TestClient):
    """Verifies that POST /api/v1/discover is registered and does not return 404."""
    response = api_client.post("/api/v1/discover", json={"raw_input": "rohtang ki ice wali photo"})
    assert response.status_code != 404


def test_discover_endpoint_trailing_slash_compatible(api_client: TestClient):
    """Verifies that POST /api/v1/discover/ is also accessible without redirect issues."""
    response = api_client.post("/api/v1/discover/", json={"raw_input": "rohtang ki ice wali photo"})
    assert response.status_code == 200


# =============================================================================
# 2. CANONICAL QUERY EXECUTION & HTTP 200
# =============================================================================

def test_canonical_query_produces_http_200(api_client: TestClient):
    """Verifies that canonical Case 2 query produces HTTP 200 OK."""
    payload = {
        "raw_input": "rohtang ki ice wali photo",
        "top_k": 5,
        "enable_recovery": True,
    }
    response = api_client.post("/api/v1/discover", json=payload)
    assert response.status_code == 200


def test_canonical_kinship_query_produces_http_200(api_client: TestClient):
    """Verifies that canonical Case 1 query ('5 sisters') produces HTTP 200 OK."""
    payload = {
        "raw_input": "5 sisters",
        "top_k": 5,
    }
    response = api_client.post("/api/v1/discover", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["raw_input"] == "5 sisters"


# =============================================================================
# 3. SCHEMA COMPLIANCE (SECTION 18.2)
# =============================================================================

def test_response_conforms_to_section_18_2_schema(api_client: TestClient):
    """
    Verifies that the returned JSON strictly matches the Section 18.2 schema
    and can be validated into the locked DiscoveryResponse Pydantic model.
    """
    payload = {"raw_input": "rohtang ki ice wali photo", "top_k": 5}
    response = api_client.post("/api/v1/discover", json=payload)
    assert response.status_code == 200

    data = response.json()

    # Required top-level fields
    assert "raw_input" in data
    assert "v2_frame" in data
    assert "retrieval_signals" in data
    assert "coverage_status" in data
    assert "controlled_recovery_triggered" in data
    assert "candidate_pool_size" in data
    assert "results" in data

    # Validate with Pydantic model
    validated = DiscoveryResponse.model_validate(data)
    assert validated.raw_input == "rohtang ki ice wali photo"
    assert validated.candidate_pool_size > 0
    assert len(validated.results) > 0

    # Validate CandidateResult fields
    top_cand = validated.results[0]
    assert top_cand.rank == 1
    assert top_cand.score > 0.0
    assert isinstance(top_cand.score_breakdown, ScoreBreakdown)
    assert top_cand.score_breakdown.base_rrf >= 0.0
    assert "lexical_fts" in top_cand.retrieval_paths


# =============================================================================
# 4. TOP_K PARAMETER TRUNCATION
# =============================================================================

def test_top_k_parameter_is_respected(api_client: TestClient):
    """Verifies that top_k restricts the maximum number of returned candidate results."""
    for requested_k in [1, 3, 5]:
        response = api_client.post(
            "/api/v1/discover",
            json={"raw_input": "rohtang ki ice wali photo", "top_k": requested_k},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= requested_k
        if len(data["results"]) > 0:
            for idx, cand in enumerate(data["results"], start=1):
                assert cand["rank"] == idx


# =============================================================================
# 5. INPUT VALIDATION & 4XX RESPONSES
# =============================================================================

def test_empty_body_produces_422(api_client: TestClient):
    """Verifies that sending an empty JSON object returns HTTP 422 Unprocessable Entity."""
    response = api_client.post("/api/v1/discover", json={})
    assert response.status_code == 422
    assert "query" in response.text.lower() or "required" in response.text.lower()


def test_missing_query_fields_produces_422(api_client: TestClient):
    """Verifies that payload without raw_input, query, or v2_representation returns HTTP 422."""
    response = api_client.post("/api/v1/discover", json={"top_k": 5, "enable_recovery": True})
    assert response.status_code == 422


def test_negative_top_k_produces_422(api_client: TestClient):
    """Verifies that non-positive top_k produces HTTP 422."""
    response = api_client.post("/api/v1/discover", json={"raw_input": "rohtang", "top_k": -1})
    assert response.status_code == 422

    response_zero = api_client.post("/api/v1/discover", json={"raw_input": "rohtang", "top_k": 0})
    assert response_zero.status_code == 422


def test_excessive_top_k_produces_422(api_client: TestClient):
    """Verifies that top_k exceeding maximum (100) produces HTTP 422."""
    response = api_client.post("/api/v1/discover", json={"raw_input": "rohtang", "top_k": 101})
    assert response.status_code == 422


def test_invalid_type_raw_input_produces_422(api_client: TestClient):
    """Verifies that non-string raw_input produces HTTP 422."""
    response = api_client.post("/api/v1/discover", json={"raw_input": 12345})
    assert response.status_code == 422


# =============================================================================
# 6. PIPELINE INVOCATION (NOT DUPLICATE LOGIC)
# =============================================================================

def test_endpoint_invokes_discovery_engine_pipeline(api_client: TestClient):
    """
    Verifies that the endpoint calls DiscoveryEnginePipeline.run()
    rather than re-implementing retrieval logic.
    """
    mock_response = DiscoveryResponse(
        raw_input="mocked query",
        v2_frame={"raw_input": "mocked query"},
        retrieval_signals={"search_query_terms": ["mocked"]},
        coverage_status="COVERAGE_SUFFICIENT",
        controlled_recovery_triggered=False,
        candidate_pool_size=1,
        results=[
            CandidateResult(
                candidate_id="mock_chunk_1",
                chunk_id="mock_chunk_1",
                case_id="case_mock",
                content="Mocked retrieval content",
                rank=1,
                score=2.0,
                score_breakdown=ScoreBreakdown(
                    base_rrf=0.5,
                    bound_bonus=1.5,
                    distractor_penalty=0.0,
                ),
                retrieval_paths=["lexical_fts"],
                metadata={},
            )
        ],
    )

    with patch.object(DiscoveryEnginePipeline, "run", new_callable=AsyncMock) as mock_run:
        mock_run.return_value = mock_response

        response = api_client.post(
            "/api/v1/discover",
            json={"raw_input": "mocked query", "top_k": 5},
        )

        assert response.status_code == 200
        assert mock_run.await_count == 1
        call_kwargs = mock_run.call_args.kwargs
        assert call_kwargs["query"] == "mocked query"
        assert call_kwargs["top_k"] == 5

        data = response.json()
        assert data["raw_input"] == "mocked query"
        assert len(data["results"]) == 1
        assert data["results"][0]["candidate_id"] == "mock_chunk_1"


# =============================================================================
# 7. STRUCTURED V2 REPRESENTATION PASSTHROUGH
# =============================================================================

def test_endpoint_supports_pre_parsed_v2_representation(api_client: TestClient):
    """
    Verifies that a pre-parsed V2MemoryRepresentation passed in request
    is forwarded directly to the pipeline.
    """
    v2_input = {
        "raw_input": "5 sisters photo",
        "people": [{"role": "sister", "count": 5, "attributes": [], "possessive": None}],
        "events": None,
        "objects": [],
        "actions": [],
        "temporal": None,
        "literal_text": [],
        "spatial_setting": None,
    }
    payload = {
        "v2_representation": v2_input,
        "top_k": 3,
    }

    response = api_client.post("/api/v1/discover", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["raw_input"] == "5 sisters photo"
    assert data["v2_frame"]["people"][0]["role"] == "sister"
    assert data["v2_frame"]["people"][0]["count"] == 5


# =============================================================================
# 8. RETRIEVAL FILTER FORWARDING
# =============================================================================

def test_endpoint_supports_retrieval_filters(api_client: TestClient):
    """
    Verifies that structured filters (rating, category_tags) are parsed
    and applied by the pipeline.
    """
    payload = {
        "raw_input": "google photos update search",
        "filters": {
            "rating": 1,
        },
        "top_k": 3,
    }

    response = api_client.post("/api/v1/discover", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_pool_size"] > 0
    for cand in data["results"]:
        assert cand["metadata"].get("rating") == 1
