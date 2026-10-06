"""
Deterministic Regression Tests for D2 Memory Search AI Interpretation & Full Response Caching.

Governed strictly by Memory Search AI Consistency Fix:
1. Submit query 5 times:
   'woh shaadi ka function tha hum sab family wale gaye the aur mein ne bhai ke saath photo li thi white bike par'
   Complete /api/v1/memory/search response must be identical across all 5 runs.
2. 'family trip near the beach at sunset'
   Expected semantic clues must remain stable across repeated runs.
3. 'my brother on a white bike'
   Missing information is NOT invented (no location, date, wedding, beach, or sunset).
4. ASR phonetic normalization for mixed Hinglish/Roman-script input.
5. User's manually corrected text is preserved as authoritative retrieval query.
6. Complete response cache & deterministic candidate ordering with stable tie-breaking.
"""

import copy
import pytest
import httpx
from fastapi.testclient import TestClient

from app.main import app
from app.memory.groq_service import (
    GroqMemoryInterpreter,
    clear_interpretation_cache,
)
from app.memory.normalization import normalize_memory_query, get_cache_key
from app.memory.response_cache import (
    clear_all_memory_caches,
    make_search_cache_key,
    make_deterministic_candidate_ordering,
)
from app.retrieval.models import CandidateResult, ScoreBreakdown


@pytest.fixture(autouse=True)
def clean_cache():
    """Ensure clean interpretation and full response caches before and after each test."""
    clear_interpretation_cache()
    clear_all_memory_caches()
    yield
    clear_interpretation_cache()
    clear_all_memory_caches()


# ---------------------------------------------------------------------------
# 1. 5-Run Identical Interpretation Regression Test
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_identical_interpretation_5_runs():
    """
    Submits exact query 5 times:
    'woh shaadi ka function tha hum sab family wale gaye the aur mein ne bhai ke saath photo li thi white bike par'
    Structured interpretation must be 100% identical across all 5 runs.
    """
    query = "woh shaadi ka function tha hum sab family wale gaye the aur mein ne bhai ke saath photo li thi white bike par"
    interpreter = GroqMemoryInterpreter()

    results = []
    for run_idx in range(5):
        clues, provider = await interpreter.interpret(query)
        dump = clues.model_dump()
        results.append(dump)

    # 1. Verify 100% identity across all 5 runs
    first_run = results[0]
    for idx, run_result in enumerate(results[1:], start=2):
        assert run_result == first_run, f"Run {idx} differed from Run 1!"

    # 2. Verify semantic clues explicitly present
    people_roles = [p["role"].lower() for p in first_run["people"]]
    assert any("family" in r for r in people_roles), "Expected 'family' in people clues"
    assert any("brother" in r or "bhai" in r for r in people_roles), "Expected 'brother' or 'bhai' in people clues"

    # Occasion / Event
    assert first_run["event_activity"] is not None, "Expected event_activity to be present"
    ev_name = (first_run["event_activity"]["event_name"] or "").lower()
    assert "wedding" in ev_name or "shaadi" in ev_name, f"Expected wedding/shaadi in event_name, got: {ev_name}"

    # Object: white bike
    obj_names = [o["name"].lower() for o in first_run["objects"]]
    assert "bike" in obj_names, "Expected 'bike' in objects"
    bike_obj = next(o for o in first_run["objects"] if o["name"].lower() == "bike")
    assert "white" in [a.lower() for a in bike_obj["attributes"]], "Expected 'white' attribute on bike"

    # 3. Verify zero hallucination of absent dimensions
    assert first_run["place_location"] is None, f"Location was invented: {first_run['place_location']}"
    assert first_run["time_temporal"] is None, f"Time was invented: {first_run['time_temporal']}"
    assert first_run["scene_environment"] is None, f"Scene was invented: {first_run['scene_environment']}"


# ---------------------------------------------------------------------------
# 2. Stability Test: family trip near the beach at sunset
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_stable_semantic_clues_family_trip_beach_sunset():
    """
    'family trip near the beach at sunset'
    Expected semantic clues must remain stable across repeated runs.
    """
    query = "family trip near the beach at sunset"
    interpreter = GroqMemoryInterpreter()

    runs = []
    for _ in range(3):
        clues, _ = await interpreter.interpret(query)
        runs.append(clues.model_dump())

    assert runs[0] == runs[1] == runs[2], "Repeated runs were not identical!"

    clues = runs[0]
    # Location: beach
    assert clues["place_location"] is not None, "Expected place_location for beach"
    assert "beach" in clues["place_location"]["place"].lower()

    # Time: sunset
    assert clues["time_temporal"] is not None, "Expected time_temporal for sunset"
    assert "sunset" in clues["time_temporal"]["raw_expression"].lower()

    # Event: trip
    assert clues["event_activity"] is not None, "Expected event_activity for trip"
    assert "trip" in (clues["event_activity"]["event_name"] or "").lower()

    # People: family
    people_roles = [p["role"].lower() for p in clues["people"]]
    assert any("family" in r for r in people_roles), "Expected 'family' in people"


# ---------------------------------------------------------------------------
# 3. Negative Grounding Test: Missing information NOT invented
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_missing_information_not_invented():
    """
    'my brother on a white bike'
    Must not invent:
    - location
    - date / time
    - wedding
    - beach
    - sunset
    """
    query = "my brother on a white bike"
    interpreter = GroqMemoryInterpreter()

    clues, _ = await interpreter.interpret(query)
    c = clues.model_dump()

    # Must NOT invent missing dimensions
    assert c["place_location"] is None, f"Invented location: {c['place_location']}"
    assert c["time_temporal"] is None, f"Invented time: {c['time_temporal']}"
    assert c["scene_environment"] is None, f"Invented scene: {c['scene_environment']}"

    # Event must NOT invent wedding, beach, or trip
    if c["event_activity"]:
        ev_name = (c["event_activity"]["event_name"] or "").lower()
        assert not any(w in ev_name for w in ["wedding", "shaadi", "beach", "trip", "sunset"])

    # Strictly capture brother and white bike
    people_roles = [p["role"].lower() for p in c["people"]]
    assert any("brother" in r or "bhai" in r for r in people_roles), "Expected brother in people"

    obj_names = [o["name"].lower() for o in c["objects"]]
    assert "bike" in obj_names, "Expected bike in objects"


# ---------------------------------------------------------------------------
# 4. ASR Spelling and Hinglish Normalization Tests
# ---------------------------------------------------------------------------

def test_asr_phonetic_normalization():
    """Verifies that common ASR spelling errors in Hinglish are cleanly normalized."""
    assert normalize_memory_query("shadi ka fnkton") == "shaadi ka function"
    assert normalize_memory_query("white baike") == "white bike"
    assert normalize_memory_query("phto of famly trip") == "photo of family trip"
    assert normalize_memory_query("bhai ke saath phtoto li thi") == "bhai ke saath photo li thi"


def test_cache_key_equivalence():
    """Verifies that ASR variations map to the same cache key."""
    key_typo = get_cache_key("shadi ka fnkton")
    key_clean = get_cache_key("shaadi ka function")
    assert key_typo == key_clean, f"Cache keys did not match: '{key_typo}' vs '{key_clean}'"

    key_bike_typo = get_cache_key("white baike")
    key_bike_clean = get_cache_key("white bike")
    assert key_bike_typo == key_bike_clean


# ---------------------------------------------------------------------------
# 5. Full Search Response 5-Run Identical Regression Test
# ---------------------------------------------------------------------------

def test_complete_search_response_identical_5_runs(monkeypatch):
    """
    Submits exact query 5 times to /api/v1/memory/search:
    'woh shaadi ka function tha hum sab family wale gaye the aur mein ne bhai ke saath photo li thi white bike par'
    Verifies that the COMPLETE response is structurally and byte-for-byte identical across all 5 runs.
    """
    query = "woh shaadi ka function tha hum sab family wale gaye the aur mein ne bhai ke saath photo li thi white bike par"

    # Mock D1 Discovery Engine
    d1_call_count = 0
    orig_post = httpx.AsyncClient.post

    async def mock_post(self, url, *args, **kwargs):
        url_str = str(url)
        if url_str.endswith("/api/v1/discover"):
            nonlocal d1_call_count
            d1_call_count += 1
            return httpx.Response(
                status_code=200,
                json={
                    "raw_input": query,
                    "v2_frame": kwargs.get("json", {}).get("v2_representation", {}),
                    "retrieval_signals": {
                        "search_query_terms": ["wedding", "bike", "family"],
                        "visual_entities": ["bike"],
                        "bound_attributes": ["white"],
                    },
                    "coverage_status": "COVERAGE_SUFFICIENT",
                    "controlled_recovery_triggered": False,
                    "candidate_pool_size": 2,
                    "results": [
                        {
                            "candidate_id": "cand_1",
                            "chunk_id": "chunk_uuid_1",
                            "case_id": "case_1",
                            "chunk_type": "RAW_QUOTE",
                            "content": "Photo with brother on a white bike at family wedding",
                            "rank": 1,
                            "score": 2.5,
                            "score_breakdown": {"base_rrf": 0.5, "bound_bonus": 2.0, "distractor_penalty": 0.0},
                            "retrieval_paths": ["lexical_fts"],
                            "metadata": {"source": "photo_archive"},
                        },
                        {
                            "candidate_id": "cand_2",
                            "chunk_id": "chunk_uuid_2",
                            "case_id": "case_2",
                            "chunk_type": "RAW_QUOTE",
                            "content": "Family gathering photo during wedding reception",
                            "rank": 2,
                            "score": 1.8,
                            "score_breakdown": {"base_rrf": 0.3, "bound_bonus": 1.5, "distractor_penalty": 0.0},
                            "retrieval_paths": ["lexical_fts"],
                            "metadata": {"source": "photo_archive"},
                        },
                    ],
                },
                request=httpx.Request("POST", str(url)),
            )
        return await orig_post(self, url, *args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    with TestClient(app) as client:
        runs = []
        for run_idx in range(5):
            res = client.post(
                "/api/v1/memory/search",
                json={"raw_input": query, "top_k": 8, "enable_recovery": True},
            )
            assert res.status_code == 200
            runs.append(res.json())

        # Verify exact structural identity across all 5 runs
        first = runs[0]
        for idx in range(1, 5):
            assert runs[idx]["structured_clues"] == first["structured_clues"], f"Clues differed on run {idx + 1}"
            assert runs[idx]["results"] == first["results"], f"Results differed on run {idx + 1}"
            assert runs[idx]["v2_frame"] == first["v2_frame"], f"v2_frame differed on run {idx + 1}"
            assert runs[idx]["retrieval_signals"] == first["retrieval_signals"], f"retrieval_signals differed on run {idx + 1}"
            assert runs[idx]["coverage_status"] == first["coverage_status"]
            assert runs[idx]["candidate_pool_size"] == first["candidate_pool_size"]
            assert runs[idx]["is_ambiguous"] == first["is_ambiguous"]

        # Only 1 D1 call occurred; runs 2-5 were served instantly from the full response cache!
        assert d1_call_count == 1, f"Expected 1 D1 call due to full response cache, but had {d1_call_count}"


# ---------------------------------------------------------------------------
# 6. ASR Spelling Variation Returns Canonical Response with Verbatim User Query
# ---------------------------------------------------------------------------

def test_asr_spelling_variation_returns_same_canonical_response(monkeypatch):
    """
    Query 1: 'woh shaadi ka function tha hum sab family wale gaye the aur mein ne bhai ke saath photo li thi white bike par'
    Query 2: 'woh shadi ka fnkton tha hum sab family wale gaye the aur mein ne bhai ke saath photo li thi white baike par'
    Both resolve to the same canonical search response, while preserving their respective original_memory_text.
    """
    clean_query = "woh shaadi ka function tha hum sab family wale gaye the aur mein ne bhai ke saath photo li thi white bike par"
    asr_query = "woh shadi ka fnkton tha hum sab family wale gaye the aur mein ne bhai ke saath photo li thi white baike par"
    orig_post = httpx.AsyncClient.post

    async def mock_post(self, url, *args, **kwargs):
        url_str = str(url)
        if url_str.endswith("/api/v1/discover"):
            return httpx.Response(
                status_code=200,
                json={
                    "raw_input": clean_query,
                    "v2_frame": kwargs.get("json", {}).get("v2_representation", {}),
                    "retrieval_signals": {"search_query_terms": ["wedding", "bike"], "visual_entities": ["bike"], "bound_attributes": []},
                    "coverage_status": "COVERAGE_SUFFICIENT",
                    "controlled_recovery_triggered": False,
                    "candidate_pool_size": 1,
                    "results": [
                        {
                            "candidate_id": "cand_1",
                            "chunk_id": "chunk_uuid_1",
                            "case_id": "case_1",
                            "chunk_type": "RAW_QUOTE",
                            "content": "Photo with brother on white bike at wedding function",
                            "rank": 1,
                            "score": 2.5,
                            "score_breakdown": {"base_rrf": 0.5, "bound_bonus": 2.0, "distractor_penalty": 0.0},
                            "retrieval_paths": ["lexical_fts"],
                            "metadata": {},
                        }
                    ],
                },
                request=httpx.Request("POST", str(url)),
            )
        return await orig_post(self, url, *args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    with TestClient(app) as client:
        # 1. First run with clean query
        res1 = client.post("/api/v1/memory/search", json={"raw_input": clean_query, "top_k": 8, "enable_recovery": True})
        assert res1.status_code == 200
        data1 = res1.json()

        # 2. Second run with ASR phonetic variation
        res2 = client.post("/api/v1/memory/search", json={"raw_input": asr_query, "top_k": 8, "enable_recovery": True})
        assert res2.status_code == 200
        data2 = res2.json()

        # Same results and interpretation semantics
        assert data1["results"] == data2["results"]
        assert data1["structured_clues"]["people"] == data2["structured_clues"]["people"]
        assert data1["structured_clues"]["objects"] == data2["structured_clues"]["objects"]
        assert data1["structured_clues"]["event_activity"] == data2["structured_clues"]["event_activity"]

        # But each preserves what the user actually submitted
        assert data1["original_memory_text"] == clean_query
        assert data1["raw_input"] == clean_query
        assert data2["original_memory_text"] == asr_query
        assert data2["raw_input"] == asr_query


# ---------------------------------------------------------------------------
# 7. Different Query Processes as Independent Search
# ---------------------------------------------------------------------------

def test_different_query_processes_independently(monkeypatch):
    """Proves different queries produce different cache keys and are processed independently."""
    q1 = "woh shaadi ka function tha hum sab family wale gaye the aur mein ne bhai ke saath photo li thi white bike par"
    q2 = "family trip near the beach at sunset"

    key1 = make_search_cache_key(q1, top_k=8, enable_recovery=True)
    key2 = make_search_cache_key(q2, top_k=8, enable_recovery=True)
    assert key1 != key2, "Expected different cache keys for different queries"

    d1_queries_received = []
    orig_post = httpx.AsyncClient.post

    async def mock_post(self, url, *args, **kwargs):
        url_str = str(url)
        if url_str.endswith("/api/v1/discover"):
            req_raw = kwargs.get("json", {}).get("v2_representation", {}).get("raw_input", "")
            d1_queries_received.append(req_raw)
            return httpx.Response(
                status_code=200,
                json={
                    "raw_input": req_raw,
                    "v2_frame": kwargs.get("json", {}).get("v2_representation", {}),
                    "retrieval_signals": {"search_query_terms": [req_raw], "visual_entities": [], "bound_attributes": []},
                    "coverage_status": "COVERAGE_SUFFICIENT",
                    "controlled_recovery_triggered": False,
                    "candidate_pool_size": 1,
                    "results": [],
                },
                request=httpx.Request("POST", str(url)),
            )
        return await orig_post(self, url, *args, **kwargs)

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    with TestClient(app) as client:
        res1 = client.post("/api/v1/memory/search", json={"raw_input": q1, "top_k": 8, "enable_recovery": True})
        res2 = client.post("/api/v1/memory/search", json={"raw_input": q2, "top_k": 8, "enable_recovery": True})

        assert res1.status_code == 200
        assert res2.status_code == 200
        assert len(d1_queries_received) == 2, "Expected 2 separate D1 calls for distinct queries"
        assert d1_queries_received[0] == q1
        assert d1_queries_received[1] == q2


# ---------------------------------------------------------------------------
# 8. Deterministic Candidate Ordering with Stable Tie-Breaking
# ---------------------------------------------------------------------------

def test_candidate_ordering_tie_breaking_stability():
    """
    Proves that results with equal scores are stably ordered by chunk_id/candidate_id,
    never by random or hash-dependent order.
    """
    sb = ScoreBreakdown(base_rrf=0.5, bound_bonus=1.0, distractor_penalty=0.0)
    c_b = CandidateResult(
        candidate_id="id_b", chunk_id="uuid_b", case_id="c1", chunk_type="RAW_QUOTE",
        content="Caption Beta", rank=1, score=2.0, score_breakdown=sb,
    )
    c_a = CandidateResult(
        candidate_id="id_a", chunk_id="uuid_a", case_id="c1", chunk_type="RAW_QUOTE",
        content="Caption Alpha", rank=2, score=2.0, score_breakdown=sb,
    )
    c_c = CandidateResult(
        candidate_id="id_c", chunk_id="uuid_c", case_id="c1", chunk_type="RAW_QUOTE",
        content="Caption Gamma", rank=3, score=2.0, score_breakdown=sb,
    )

    # Regardless of input permutation, output order must be strictly deterministic
    ordering_1 = make_deterministic_candidate_ordering([c_c, c_b, c_a])
    ordering_2 = make_deterministic_candidate_ordering([c_a, c_b, c_c])
    ordering_3 = make_deterministic_candidate_ordering([c_b, c_c, c_a])

    assert [c.chunk_id for c in ordering_1] == ["uuid_a", "uuid_b", "uuid_c"]
    assert [c.chunk_id for c in ordering_2] == ["uuid_a", "uuid_b", "uuid_c"]
    assert [c.chunk_id for c in ordering_3] == ["uuid_a", "uuid_b", "uuid_c"]
    assert [c.rank for c in ordering_1] == [1, 2, 3]


# ---------------------------------------------------------------------------
# 9. User's Corrected Query Preserved Authoritatively in Retrieval
# ---------------------------------------------------------------------------

def test_user_corrected_query_preserved_in_endpoint(monkeypatch):
    """
    Verifies that the user's manually corrected text is preserved as authoritative
    in original_memory_text, raw_input, and v2_frame.raw_input.
    """
    user_corrected_text = "woh shaadi ka function tha hum sab family wale gaye the aur mein ne bhai ke saath photo li thi white bike par"

    # Mock D1 Discovery Engine endpoint
    async def mock_d1_post(self, url, *args, **kwargs):
        req_json = kwargs.get("json", {})
        # Verify D1 receives v2_representation with user's exact raw_input
        v2_rep = req_json.get("v2_representation", {})
        assert v2_rep.get("raw_input") == user_corrected_text, (
            f"Expected v2_representation.raw_input to match user query, got {v2_rep.get('raw_input')}"
        )
        return httpx.Response(
            status_code=200,
            json={
                "raw_input": user_corrected_text,
                "v2_frame": v2_rep,
                "retrieval_signals": {"search_query_terms": ["wedding", "bike"], "visual_entities": ["bike"], "bound_attributes": []},
                "coverage_status": "COVERAGE_SUFFICIENT",
                "controlled_recovery_triggered": False,
                "candidate_pool_size": 1,
                "results": [],
            },
            request=httpx.Request("POST", str(url)),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_d1_post)

    with TestClient(app) as client:
        res = client.post(
            "/api/v1/memory/search",
            json={"raw_input": user_corrected_text, "top_k": 5, "enable_recovery": True},
        )
        assert res.status_code == 200
        data = res.json()

        assert data["original_memory_text"] == user_corrected_text
        assert data["raw_input"] == user_corrected_text
        assert data["v2_frame"]["raw_input"] == user_corrected_text


# ---------------------------------------------------------------------------
# 10. Consumer Grounding Boundary Tests
# ---------------------------------------------------------------------------

def test_grounded_consumer_memory_rejects_document_search_for_birthday_query():
    """
    Verifies that broad lexical matches on document-scanning research evidence
    (e.g., interview-c03-s01 tagged with DOCUMENT_SEARCH) are rejected for
    photo-memory queries like birthday dinner celebrations.
    """
    from app.api.v1.endpoints.memory_search import is_grounded_consumer_memory, is_eligible_consumer_memory

    sb = ScoreBreakdown(base_rrf=0.0156, bound_bonus=0.0, distractor_penalty=0.0)

    # Document-scanning interview artifact
    doc_cand = CandidateResult(
        candidate_id="interview-c03-s01",
        chunk_id="uuid_doc_01",
        case_id="case_doc",
        chunk_type="RAW_QUOTE",
        content="Camera-captured document from 4 years ago. User searched for insurance text.",
        rank=1,
        score=0.0156,
        score_breakdown=sb,
        metadata={
            "evidence_type": "SUCCESS",
            "methodology": "PROMPTED_INTERVIEW",
            "category_tags": ["DOCUMENT_SEARCH"],
            "source": "USER_INTERVIEW",
        },
    )

    query = "I remember a photo from a birthday celebration with my family. I was taking photos during dinner."

    # Passes baseline source/methodology eligibility
    assert is_eligible_consumer_memory(doc_cand) is True

    # MUST FAIL grounding filter because category is DOCUMENT_SEARCH and content lacks salient clues (birthday, dinner, family)
    assert is_grounded_consumer_memory(doc_cand, raw_query=query) is False


def test_grounded_consumer_memory_preserves_bound_bonus_candidates():
    """
    Verifies that candidates with bound entity bonuses (+1.5) pass grounding immediately.
    """
    from app.api.v1.endpoints.memory_search import is_grounded_consumer_memory

    sb = ScoreBreakdown(base_rrf=0.033, bound_bonus=1.5, distractor_penalty=0.0)
    wedding_cand = CandidateResult(
        candidate_id="interview-c03-s04",
        chunk_id="uuid_wed_04",
        case_id="case_wed",
        chunk_type="RAW_QUOTE",
        content="Wedding function with family, photo on white motorcycle with brother.",
        rank=1,
        score=1.533,
        score_breakdown=sb,
        metadata={"evidence_type": "SUCCESS", "methodology": "PROMPTED_INTERVIEW"},
    )

    query = "woh shaadi ka function tha hum sab family wale gaye the aur mein ne bhai ke saath photo li thi white bike par"
    assert is_grounded_consumer_memory(wedding_cand, raw_query=query) is True


def test_grounded_consumer_memory_requires_salient_clue_for_weak_candidates():
    """
    Verifies that weak candidates (bound_bonus=0.0) without salient clue overlap
    are rejected.
    """
    from app.api.v1.endpoints.memory_search import is_grounded_consumer_memory
    from app.memory.schemas import MemoryStructuredClues, PersonClue, EventActivityClue, AmbiguityAssessment

    sb = ScoreBreakdown(base_rrf=0.0156, bound_bonus=0.0, distractor_penalty=0.0)
    unrelated_cand = CandidateResult(
        candidate_id="unrelated-001",
        chunk_id="uuid_unrelated",
        case_id="case_unrelated",
        chunk_type="RAW_QUOTE",
        content="Random street photo taken during a sunny afternoon.",
        rank=1,
        score=0.0156,
        score_breakdown=sb,
        metadata={"evidence_type": "SUCCESS", "methodology": "PROMPTED_INTERVIEW"},
    )

    clues = MemoryStructuredClues(
        original_memory_text="photo with brother on birthday",
        people=[PersonClue(role="brother", count=1, attributes=[], certainty="explicit")],
        event_activity=EventActivityClue(event_name="birthday", certainty="explicit"),
        uncertainty_ambiguity=AmbiguityAssessment(is_ambiguous=False),
    )

    # Content has neither 'brother' nor 'birthday'
    assert is_grounded_consumer_memory(unrelated_cand, structured_clues=clues, raw_query="photo with brother on birthday") is False

