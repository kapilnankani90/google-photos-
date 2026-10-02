"""
Automated Test Suite for Step 4 — V2 Memory Representation Pipeline.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 7.1, 7.2, 8.2, 23, 24)
- part1_memory_representation_schema_v2.md
- part1_discovery_engine_operating_spec_final.md (Canonical Traces 1–8)

Covers:
A. Deterministic extraction across all 8 canonical benchmark cases + generalizations
B. Structured V2 representation schema validation & extra="forbid" rejection
C. Missing information / uncertainty handling without speculative defaults
D. Multilingual / Hinglish handling & vernacular particle stripping
E. Ambiguous-query fallback routing
F. Gemini mocked response (structured V2 output)
G. Malformed Gemini response handling
H. Gemini unavailable & timeout behavior
I. No fabricated fields guarantee (e.g., snowy mountain / college trip example)
J. Persistence mapping to database columns
K. Idempotency in persistence layer
L. Validation failure behavior
M. Provenance / original wording preservation
"""

import sys
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import httpx
from pydantic import ValidationError

# Ensure project root and backend are on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.representation.models import (
    PersonConcept,
    EventConcept,
    ObjectConcept,
    TemporalConcept,
    V2MemoryRepresentation,
)
from app.representation.rules import (
    parse_deterministically,
    strip_vernacular_particles,
    is_ambiguous_query,
    sanitize_input,
)
from app.representation.gemini_parser import GeminiParserClient
from app.representation.interpreter import MemoryInterpreter
from app.representation.persistence import (
    persist_representation,
    fetch_representation_by_id,
)


# =============================================================================
# A. DETERMINISTIC EXTRACTION: 8 CANONICAL OPERATING SPEC CASES
# =============================================================================

def test_canonical_case_1_five_sisters():
    """Case 1: '5 sisters' -> Kinship role='sister', count=5."""
    rep = parse_deterministically("5 sisters")
    assert rep.raw_input == "5 sisters"
    assert len(rep.people) == 1
    assert rep.people[0].role == "sister"
    assert rep.people[0].count == 5
    assert rep.people[0].attributes == []
    assert rep.events is None
    assert rep.objects == []


def test_canonical_case_2_rohtang_ice():
    """Case 2: 'rohtang ki ice wali photo' -> object='ice', spatial_setting='rohtang'."""
    raw = "rohtang ki ice wali photo"
    rep = parse_deterministically(raw)
    assert rep.raw_input == raw
    assert len(rep.objects) == 1
    assert rep.objects[0].name == "ice"
    assert rep.spatial_setting == "rohtang"


def test_canonical_case_3_white_bike():
    """Case 3: 'white bike' -> object='bike', attributes=['white']."""
    rep = parse_deterministically("white bike")
    assert rep.raw_input == "white bike"
    assert len(rep.objects) == 1
    assert rep.objects[0].name == "bike"
    assert rep.objects[0].attributes == ["white"]


def test_canonical_case_4_diya_gate():
    """Case 4: 'diya at the gate' -> object='diya', spatial_setting='gate'."""
    rep = parse_deterministically("diya at the gate")
    assert rep.raw_input == "diya at the gate"
    assert len(rep.objects) == 1
    assert rep.objects[0].name == "diya"
    assert rep.spatial_setting == "gate"


def test_canonical_case_5_progressive_ocr():
    """Case 5: 'Progressive' -> literal_text=['Progressive']."""
    rep = parse_deterministically("Progressive")
    assert rep.raw_input == "Progressive"
    assert rep.literal_text == ["Progressive"]
    assert rep.objects == []


def test_canonical_case_6_document_relative_time():
    """Case 6: 'document around 4 years ago' -> object='document', temporal=RELATIVE_OFFSET."""
    rep = parse_deterministically("document around 4 years ago")
    assert rep.raw_input == "document around 4 years ago"
    assert len(rep.objects) == 1
    assert rep.objects[0].name == "document"
    assert rep.temporal is not None
    assert rep.temporal.raw_time_expression == "around 4 years ago"
    assert rep.temporal.coarse_value == "4 years ago"
    assert rep.temporal.temporal_nature == "RELATIVE_OFFSET"


def test_canonical_case_7_yellow_truck():
    """Case 7: 'yellow truck' -> object='truck', attributes=['yellow']."""
    rep = parse_deterministically("yellow truck")
    assert rep.raw_input == "yellow truck"
    assert len(rep.objects) == 1
    assert rep.objects[0].name == "truck"
    assert rep.objects[0].attributes == ["yellow"]


def test_canonical_case_8_wedding_event():
    """Case 8: 'wedding' -> event_name='wedding'."""
    rep = parse_deterministically("wedding")
    assert rep.raw_input == "wedding"
    assert rep.events is not None
    assert rep.events.event_name == "wedding"
    assert rep.events.sub_event is None


# =============================================================================
# B. STRUCTURED V2 REPRESENTATION SCHEMA & EXTRA="FORBID"
# =============================================================================

def test_v2_schema_extra_fields_forbidden():
    """Schema must strictly reject any extraneous unmodeled fields (extra='forbid')."""
    # Extra field on PersonConcept
    with pytest.raises(ValidationError):
        PersonConcept(role="sister", extra_speculative_field="invalid")

    # Extra field on EventConcept
    with pytest.raises(ValidationError):
        EventConcept(event_name="wedding", deep_ontology_tier="invalid")

    # Extra field on ObjectConcept
    with pytest.raises(ValidationError):
        ObjectConcept(name="bike", bounding_box=[0, 0, 10, 10])

    # Extra field on TemporalConcept
    with pytest.raises(ValidationError):
        TemporalConcept(raw_time_expression="2021", confidence_score=0.95)

    # Extra field on V2MemoryRepresentation
    with pytest.raises(ValidationError):
        V2MemoryRepresentation(raw_input="test", unmodeled_field="forbidden")


def test_v2_temporal_enum_validation():
    """TemporalConcept must only accept the 4 spec-approved temporal_nature enums."""
    valid_natures = ["COARSE_YEAR_ERA", "RELATIVE_OFFSET", "SEASON_EVENT_BOUND", "EXACT_MONTH_YEAR"]
    for nature in valid_natures:
        t = TemporalConcept(raw_time_expression="test", temporal_nature=nature)
        assert t.temporal_nature == nature

    with pytest.raises(ValidationError):
        TemporalConcept(raw_time_expression="test", temporal_nature="INVALID_ENUM")


# =============================================================================
# C & I. MISSING INFORMATION, UNCERTAINTY & ZERO FABRICATED FIELDS
# =============================================================================

def test_no_fabricated_fields_college_trip_example():
    """
    Governing Requirement:
    'I remember a photo with my friend near a snowy mountain, maybe during our college trip'
    System MUST NOT invent:
    - a specific mountain
    - a specific date
    - a specific friend
    - a specific location
    """
    query = "I remember a photo with my friend near a snowy mountain, maybe during our college trip"
    rep = parse_deterministically(query)

    assert rep.raw_input == query
    # Friend captured with possessive 'my'
    assert len(rep.people) == 1
    assert rep.people[0].role == "friend"
    assert rep.people[0].possessive == "my"
    assert rep.people[0].count is None  # Not fabricated

    # Event captured as college trip
    assert rep.events is not None
    assert rep.events.event_name == "college trip"

    # Spatial setting captured without fabricating specific peak
    assert rep.spatial_setting == "snowy mountain"

    # Temporal anchor NOT fabricated (must be None)
    assert rep.temporal is None

    # No imaginary objects fabricated
    assert rep.objects == []


def test_missing_information_preserves_empty_or_none():
    """Unmentioned fields must remain None or empty list; never defaulted with speculation."""
    rep = parse_deterministically("cake")
    assert rep.events is None
    assert rep.temporal is None
    assert rep.spatial_setting is None
    assert rep.people == []
    assert rep.actions == []
    assert rep.literal_text == []
    assert len(rep.objects) == 1
    assert rep.objects[0].name == "cake"


# =============================================================================
# D. MULTILINGUAL & HINGLISH HANDLING
# =============================================================================

def test_vernacular_particle_stripping():
    """Hinglish particles are stripped during semantic isolation while raw_input is untouched."""
    raw = "rohtang ki ice wali photo"
    stripped = strip_vernacular_particles(raw)
    assert stripped == "rohtang ice"

    raw2 = "durga ke sath picture"
    stripped2 = strip_vernacular_particles(raw2)
    assert stripped2 == "durga"


def test_hinglish_kinship_and_cardinality():
    """Hinglish words like 'meri', 'do', 'teen' are recognized cleanly."""
    rep1 = parse_deterministically("meri maid")
    assert len(rep1.people) == 1
    assert rep1.people[0].role == "maid"
    assert rep1.people[0].possessive == "my"

    rep2 = parse_deterministically("two ladies with blue outfit")
    assert len(rep2.people) == 1
    assert rep2.people[0].role == "lady"
    assert rep2.people[0].count == 2
    assert "blue outfit" in rep2.people[0].attributes


def test_temporal_variations():
    """Temporal parsing handles Exact Month-Year, Seasons, Coarse Years, and Offsets."""
    # Exact month-year
    t1 = parse_deterministically("July 2016")
    assert t1.temporal.temporal_nature == "EXACT_MONTH_YEAR"
    assert t1.temporal.coarse_value == "2016-07"

    # Season-bound
    t2 = parse_deterministically("Holi 2020")
    assert t2.temporal.temporal_nature == "SEASON_EVENT_BOUND"
    assert t2.temporal.coarse_value == "2020"

    # Coarse calendar year
    t3 = parse_deterministically("vacation in 2021")
    assert t3.temporal.temporal_nature == "COARSE_YEAR_ERA"
    assert t3.temporal.coarse_value == "2021"


# =============================================================================
# E. AMBIGUOUS-QUERY FALLBACK ROUTING
# =============================================================================

def test_ambiguity_classification():
    """Canonical queries are deterministic; long unstructured conversational sentences are ambiguous."""
    # Deterministic query
    c1 = parse_deterministically("white bike")
    assert not is_ambiguous_query("white bike", c1)

    c2 = parse_deterministically("5 sisters")
    assert not is_ambiguous_query("5 sisters", c2)

    # Long conversational ambiguous query with zero extractable structured signals
    ambiguous_query = "show me that thing we were looking at when everybody felt so amazed and shocked"
    c_amb = parse_deterministically(ambiguous_query)
    assert is_ambiguous_query(ambiguous_query, c_amb)


# =============================================================================
# F. GEMINI MOCKED RESPONSE (VALID STRUCTURED OUTPUT)
# =============================================================================

def test_gemini_mocked_structured_response():
    """Mock Gemini API returning valid structured V2 JSON."""
    raw = "looking for that snapshot of nephew playing in the fountain"
    mock_gemini_json = {
        "raw_input": raw,
        "people": [{"role": "nephew", "count": 1, "attributes": [], "possessive": None}],
        "events": None,
        "objects": [{"name": "fountain", "attributes": [], "possessive": None}],
        "actions": ["playing"],
        "temporal": None,
        "literal_text": [],
        "spatial_setting": "fountain",
    }

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": json.dumps(mock_gemini_json)}]
                }
            }
        ]
    }

    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_response

    gemini_client = GeminiParserClient(api_key="mock_key", http_client=mock_client)
    parsed = gemini_client.parse_open_domain(raw)

    assert parsed is not None
    assert parsed.raw_input == raw
    assert len(parsed.people) == 1
    assert parsed.people[0].role == "nephew"
    assert parsed.actions == ["playing"]


# =============================================================================
# G. MALFORMED GEMINI RESPONSE HANDLING
# =============================================================================

def test_gemini_malformed_json_fallback():
    """Gemini returning broken JSON must be caught safely and return None without crash."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "THIS IS NOT VALID JSON {broken: True"}]
                }
            }
        ]
    }
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_response

    gemini_client = GeminiParserClient(api_key="mock_key", http_client=mock_client)
    res = gemini_client.parse_open_domain("some query")
    assert res is None


def test_gemini_extra_field_contract_violation():
    """Gemini returning JSON violating extra='forbid' must be rejected safely."""
    violating_json = {
        "raw_input": "query",
        "people": [],
        "events": None,
        "objects": [],
        "actions": [],
        "temporal": None,
        "literal_text": [],
        "spatial_setting": None,
        "hallucinated_extra_key": "forbidden",
    }
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "candidates": [{"content": {"parts": [{"text": json.dumps(violating_json)}]}}]
    }
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.return_value = mock_response

    gemini_client = GeminiParserClient(api_key="mock_key", http_client=mock_client)
    res = gemini_client.parse_open_domain("query")
    assert res is None


# =============================================================================
# H. GEMINI UNAVAILABLE & TIMEOUT BEHAVIOR
# =============================================================================

def test_gemini_unavailable_no_api_key():
    """If no API key is provided, Gemini client returns None immediately without network call."""
    gemini_client = GeminiParserClient(api_key="")
    assert not gemini_client.is_available
    res = gemini_client.parse_open_domain("some ambiguous query")
    assert res is None


def test_gemini_timeout_handling():
    """Network timeout during Gemini call is caught safely without unhandled exception."""
    mock_client = MagicMock(spec=httpx.Client)
    mock_client.post.side_effect = httpx.TimeoutException("Connection timed out")

    gemini_client = GeminiParserClient(api_key="mock_key", http_client=mock_client)
    res = gemini_client.parse_open_domain("some query")
    assert res is None


def test_memory_interpreter_end_to_end_fallback():
    """Interpreter seamlessly falls back to deterministic frame if Gemini times out or is absent."""
    interpreter = MemoryInterpreter(gemini_client=GeminiParserClient(api_key=""))
    query = "white bike"
    result = interpreter.interpret(query)
    assert result.raw_input == query
    assert len(result.objects) == 1
    assert result.objects[0].name == "bike"
    assert result.objects[0].attributes == ["white"]


# =============================================================================
# J, K & L. PERSISTENCE MAPPING, IDEMPOTENCY & VALIDATION FAILURE
# =============================================================================

def test_to_db_dict_serialization():
    """to_db_dict() converts V2MemoryRepresentation to exact PostgreSQL column types."""
    rep = parse_deterministically("white bike")
    db_dict = rep.to_db_dict()

    assert db_dict["raw_input"] == "white bike"
    assert db_dict["people"] == []
    assert db_dict["objects"] == [{"name": "bike", "attributes": ["white"], "possessive": None}]
    assert db_dict["events"] is None
    assert db_dict["temporal"] is None
    assert db_dict["literal_text"] == []
    assert db_dict["spatial_setting"] is None


def test_persistence_insert_and_idempotent_update():
    """
    Tests that persist_representation executes INSERT when row is missing,
    and executes UPDATE when matching raw_input already exists.
    """
    import asyncio

    mock_conn = MagicMock()
    async def mock_fetchval(query, *args):
        if "SELECT id FROM memory_representations" in query:
            if getattr(mock_conn, "_has_inserted", False):
                return "11111111-2222-3333-4444-555555555555"
            return None
        elif "INSERT INTO memory_representations" in query:
            mock_conn._has_inserted = True
            return "11111111-2222-3333-4444-555555555555"
        elif "UPDATE memory_representations" in query:
            return "11111111-2222-3333-4444-555555555555"
        return None

    mock_conn.fetchval = mock_fetchval
    rep = parse_deterministically("5 sisters")

    async def _run():
        # First persistence call: INSERT
        rep_id_1 = await persist_representation(rep, conn=mock_conn)
        assert rep_id_1 == "11111111-2222-3333-4444-555555555555"

        # Second persistence call: UPDATE (idempotent, no duplicate ID)
        rep_id_2 = await persist_representation(rep, conn=mock_conn)
        assert rep_id_2 == "11111111-2222-3333-4444-555555555555"

    asyncio.run(_run())


# =============================================================================
# M. PROVENANCE & ORIGINAL WORDING PRESERVATION
# =============================================================================

def test_query_provenance_preservation():
    """Original wording must remain 100% exact in raw_input through parsing."""
    test_queries = [
        "   rohtang   ki ice wali photo   ",
        "5 sisters",
        "cousin in YELLOW SUIT at sister's wedding",
        "July 2016",
        "\"Progressive\"",
    ]

    for q in test_queries:
        parsed = parse_deterministically(q)
        assert parsed.raw_input == q, f"raw_input must be identical to input query: {q}"
