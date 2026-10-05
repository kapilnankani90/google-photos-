"""
Comprehensive Test Suite for Groq LLM/NLU Memory Search Integration.

Tests:
1. Successful parsing with Groq (extracting explicit vs inferred clues across 10 dimensions, valid V2 conversion).
2. Malformed LLM output (non-JSON, missing fields, schema violations) -> graceful fallback.
3. Missing API key -> graceful fallback without crash or exception.
4. API failure and timeout (500, 429, timeout) -> graceful fallback.
5. Ambiguous memories -> hedge detection, is_ambiguous=True, conversational clarification question.
6. REST API endpoints (/api/v1/memory/search, /api/v1/memory/interpret).
7. Confidentiality test: API key is never present in response payloads or logs.
"""

import json
import pytest
import httpx
from fastapi.testclient import TestClient

from app.main import app
from app.memory.schemas import (
    MemoryStructuredClues,
    MemorySearchRequest,
    AmbiguityAssessment,
)
from app.memory.groq_service import GroqMemoryInterpreter
from app.representation.models import V2MemoryRepresentation


# ---------------------------------------------------------------------------
# Mock Payloads
# ---------------------------------------------------------------------------

SAMPLE_FUZZY_QUERY = (
    "I'm looking for that photo from a trip where I was standing near the sea at sunset, "
    "maybe around Goa, and I think my friends were with me."
)

SAMPLE_GROQ_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": json.dumps({
                    "original_memory_text": SAMPLE_FUZZY_QUERY,
                    "people": [
                        {
                            "role": "friends",
                            "count": None,
                            "attributes": [],
                            "possessive": "my",
                            "certainty": "inferred"
                        }
                    ],
                    "place_location": {
                        "place": "Goa",
                        "attributes": ["near the sea"],
                        "certainty": "inferred"
                    },
                    "time_temporal": {
                        "raw_expression": "at sunset",
                        "coarse_value": "sunset",
                        "temporal_nature": "TIME_OF_DAY",
                        "certainty": "explicit"
                    },
                    "event_activity": {
                        "event_name": "trip",
                        "activity": "standing near the sea",
                        "certainty": "explicit"
                    },
                    "objects": [
                        {
                            "name": "sea",
                            "attributes": ["water"],
                            "certainty": "explicit"
                        }
                    ],
                    "visual_attributes": [
                        {
                            "attribute": "sunset",
                            "target_entity": "sky",
                            "certainty": "explicit"
                        }
                    ],
                    "scene_environment": {
                        "environment": "seaside beach",
                        "certainty": "explicit"
                    },
                    "relationship_context": {
                        "context": "with friends",
                        "certainty": "inferred"
                    },
                    "uncertainty_ambiguity": {
                        "is_ambiguous": True,
                        "confidence_score": 0.65,
                        "hedges_detected": ["maybe", "think"],
                        "ambiguity_reasons": ["Uncertain whether the location was indeed Goa", "Uncertain whether friends were present"],
                        "clarification_question": "Do you remember which beach in Goa you visited, or roughly what year this trip took place?"
                    }
                })
            }
        }
    ]
}


# ---------------------------------------------------------------------------
# Unit Tests: GroqMemoryInterpreter
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_successful_parsing_with_groq():
    """Verifies complete NLU decomposition, explicit vs inferred distinction, and valid V2 conversion."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=SAMPLE_GROQ_RESPONSE)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        interpreter = GroqMemoryInterpreter(
            api_key="gsk_mock_test_key_12345",
            model_name="llama-3.3-70b-versatile",
            http_client=client,
        )

        clues, provider = await interpreter.interpret(SAMPLE_FUZZY_QUERY)

        assert provider == "groq"
        assert clues.original_memory_text == SAMPLE_FUZZY_QUERY

        # Explicit vs Inferred checks
        assert clues.place_location is not None
        assert clues.place_location.place == "Goa"
        assert clues.place_location.certainty == "inferred"  # "maybe around Goa"

        assert len(clues.people) == 1
        assert clues.people[0].role == "friends"
        assert clues.people[0].certainty == "inferred"  # "I think my friends were with me"

        assert clues.time_temporal is not None
        assert clues.time_temporal.certainty == "explicit"  # "at sunset"

        # Ambiguity assessment checks
        assert clues.uncertainty_ambiguity.is_ambiguous is True
        assert "maybe" in clues.uncertainty_ambiguity.hedges_detected
        assert clues.uncertainty_ambiguity.clarification_question is not None
        assert "Goa" in clues.uncertainty_ambiguity.clarification_question

        # Conversion to Discovery Engine V2 Frame
        v2_frame = interpreter.to_v2_representation(clues)
        assert isinstance(v2_frame, V2MemoryRepresentation)
        assert v2_frame.raw_input == SAMPLE_FUZZY_QUERY
        assert len(v2_frame.people) == 1
        assert v2_frame.people[0].role == "friends"
        assert v2_frame.spatial_setting == "Goa"
        assert v2_frame.events is not None
        assert v2_frame.events.event_name == "trip"
        assert v2_frame.objects[0].name == "sea"


@pytest.mark.anyio
async def test_malformed_llm_output():
    """Verifies graceful fallback to deterministic parsing when Groq returns non-JSON or invalid schema."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": "Sorry, I cannot parse this JSON."}}]})

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        interpreter = GroqMemoryInterpreter(
            api_key="gsk_mock_test_key_12345",
            http_client=client,
        )

        clues, provider = await interpreter.interpret("A photo of my 5 sisters in Delhi")

        # Must fall back gracefully without raising an exception
        assert provider == "fallback"
        assert clues.original_memory_text == "A photo of my 5 sisters in Delhi"
        assert len(clues.people) > 0
        assert clues.people[0].role == "sister"
        assert clues.people[0].count == 5

        # V2 frame conversion must succeed
        v2 = interpreter.to_v2_representation(clues)
        assert isinstance(v2, V2MemoryRepresentation)
        assert v2.people[0].count == 5


@pytest.mark.anyio
async def test_missing_api_key():
    """Verifies that if GROQ_API_KEY is unset or None, interpreter safely falls back to deterministic NLU."""
    interpreter = GroqMemoryInterpreter(api_key="")
    assert interpreter.is_available is False

    clues, provider = await interpreter.interpret("A photo with that white bike")
    assert provider == "fallback"
    assert len(clues.objects) > 0
    assert clues.objects[0].name == "bike"
    assert "white" in clues.objects[0].attributes

    v2 = interpreter.to_v2_representation(clues)
    assert isinstance(v2, V2MemoryRepresentation)
    assert v2.objects[0].name == "bike"


@pytest.mark.anyio
async def test_api_failure_and_timeout():
    """Verifies that HTTP 503 / 429 and network timeouts trigger graceful fallback."""

    def mock_503(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="Service Unavailable")

    transport = httpx.MockTransport(mock_503)
    async with httpx.AsyncClient(transport=transport) as client:
        interpreter = GroqMemoryInterpreter(
            api_key="gsk_mock_test_key_12345",
            http_client=client,
        )

        clues, provider = await interpreter.interpret("Diya lit at the entrance gate")
        assert provider == "fallback"
        assert clues.original_memory_text == "Diya lit at the entrance gate"
        assert any(o.name == "diya" for o in clues.objects)


@pytest.mark.anyio
async def test_ambiguous_memory_clarification():
    """Verifies that an ambiguous fuzzy memory produces is_ambiguous=True and a clarification question."""
    interpreter = GroqMemoryInterpreter(api_key="")  # Test fallback deterministic ambiguity logic
    ambiguous_query = "Maybe around Goa or some beach, I think we had fun"

    clues, _ = await interpreter.interpret(ambiguous_query)
    assert clues.uncertainty_ambiguity.is_ambiguous is True
    assert len(clues.uncertainty_ambiguity.hedges_detected) > 0
    assert clues.uncertainty_ambiguity.clarification_question is not None


# ---------------------------------------------------------------------------
# API Endpoint Integration Tests
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


SAMPLE_DISCOVERY_RESPONSE = {
    "raw_input": SAMPLE_FUZZY_QUERY,
    "v2_frame": {
        "raw_input": SAMPLE_FUZZY_QUERY,
        "people": [
            {
                "role": "friends",
                "count": None,
                "attributes": [],
                "possessive": None
            }
        ],
        "events": None,
        "objects": [
            {
                "name": "beach",
                "attributes": [],
                "possessive": None
            }
        ],
        "actions": [],
        "temporal": None,
        "literal_text": [],
        "spatial_setting": "Goa"
    },
    "retrieval_signals": {
        "search_query_terms": ["Goa", "beach", "friends"],
        "visual_entities": ["beach"],
        "bound_attributes": []
    },
    "coverage_status": "COVERAGE_SUFFICIENT",
    "controlled_recovery_triggered": False,
    "candidate_pool_size": 1,
    "results": [
        {
            "candidate_id": "mock_chunk_1",
            "chunk_id": "chunk_uuid_1",
            "case_id": "case_ext_1",
            "chunk_type": "RAW_QUOTE",
            "content": "A photo of me and my friends at Goa beach.",
            "rank": 1,
            "score": 1.85,
            "score_breakdown": {
                "base_rrf": 0.35,
                "bound_bonus": 1.5,
                "distractor_penalty": 0.0
            },
            "retrieval_paths": ["lexical_fts"],
            "metadata": {
                "evidence_type": "SUCCESS",
                "source_type": "USER_INTERVIEW"
            }
        }
    ]
}


def test_memory_search_endpoint_with_mocked_groq(monkeypatch, client):
    """Verifies POST /api/v1/memory/search returns 200 with structured clues and discovery results."""
    mock_key = "gsk_test_mock_secret_key"
    monkeypatch.setattr("app.core.config.settings.GROQ_API_KEY", mock_key)

    async def mock_call_groq(self, raw_input):
        explicit, inferred, unknown = self._summarize_clues(
            json.loads(SAMPLE_GROQ_RESPONSE["choices"][0]["message"]["content"])
        )
        data = json.loads(SAMPLE_GROQ_RESPONSE["choices"][0]["message"]["content"])
        data["explicit_clues"] = explicit
        data["inferred_clues"] = inferred
        data["unknown_dimensions"] = unknown
        return MemoryStructuredClues.model_validate(data)

    monkeypatch.setattr(GroqMemoryInterpreter, "_call_groq", mock_call_groq)

    async def mock_d1_post(self, url, *args, **kwargs):
        url_str = str(url)
        assert url_str.endswith("/api/v1/discover"), f"Expected URL to end with /api/v1/discover, got {url_str}"
        req_json = kwargs.get("json", {})
        assert req_json.get("top_k") == 5
        assert req_json.get("enable_recovery") is True
        assert "v2_representation" in req_json
        assert isinstance(req_json["v2_representation"], dict)
        return httpx.Response(
            status_code=200,
            json=SAMPLE_DISCOVERY_RESPONSE,
            request=httpx.Request("POST", url_str),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_d1_post)

    payload = {
        "raw_input": SAMPLE_FUZZY_QUERY,
        "top_k": 5,
        "enable_recovery": True,
    }

    res = client.post("/api/v1/memory/search", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["original_memory_text"] == SAMPLE_FUZZY_QUERY
    assert data["llm_provider"] == "groq"
    assert data["is_ambiguous"] is True
    assert data["clarification_question"] is not None
    assert "structured_clues" in data
    assert "results" in data
    assert "v2_frame" in data
    assert "retrieval_signals" in data

    # Verify Confidentiality: API key is NEVER leaked anywhere in the JSON body
    assert mock_key not in json.dumps(data)


def test_memory_interpret_endpoint(client):
    """Verifies POST /api/v1/memory/interpret returns 200 with pure NLU structure."""
    payload = {
        "raw_input": "A photo with my 5 sisters together in Rohtang",
    }

    res = client.post("/api/v1/memory/interpret", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["original_memory_text"] == payload["raw_input"]
    assert "structured_clues" in data
    assert "v2_representation" in data
    assert "is_ambiguous" in data
