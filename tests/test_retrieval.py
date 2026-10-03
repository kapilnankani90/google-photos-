"""
Automated Test Suite for Step 6 / Phase C — PostgreSQL Lexical FTS Fallback Retrieval.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 8, 10–13, 18.2, 24)
- part1_discovery_engine_architecture_final.md (Stages 3–6)

Explicitly categorizes and executes:
I.   UNIT & CONTRACT TESTS (No database network calls required)
II.  LIVE POSTGRESQL / SUPABASE TESTS (Exercises actual PostgreSQL tsvector/GIN infrastructure)
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
    CoverageEvaluation,
)
from app.retrieval.signals import generate_retrieval_signals
from app.retrieval.retriever import MultiPathRetriever
from app.embedding.embedder import LocalEmbedder


# =============================================================================
# I. UNIT & CONTRACT TESTS (Zero Network / Zero External Calls)
# =============================================================================

def test_unit_signals_derivation_and_vernacular_particle_stripping():
    """
    [Unit Test]
    Verifies that retrieval signals isolate nouns and strip Hinglish grammatical particles
    without calling external services.
    """
    rep = V2MemoryRepresentation(
        raw_input="rohtang ki ice wali photo",
        objects=[ObjectConcept(name="ice", attributes=["cold"])],
        spatial_setting="rohtang",
    )
    signals = generate_retrieval_signals(rep)

    assert "ice" in signals.visual_entities
    assert "rohtang" in signals.spatial_cues
    assert {"entity": "ice", "attribute": "cold"} in signals.bound_attributes
    # Particles 'ki' and 'wali' must be stripped from search terms
    assert "ki" not in signals.search_query_terms
    assert "wali" not in signals.search_query_terms
    assert "ice" in signals.search_query_terms
    assert "rohtang" in signals.search_query_terms


def test_unit_temporal_signals_derivation():
    """
    [Unit Test]
    Verifies coarse year expression translates into start and end datetime bounds.
    """
    rep = V2MemoryRepresentation(
        raw_input="family photo in 2021",
        events=EventConcept(event_name="family gathering"),
        temporal=TemporalConcept(
            raw_time_expression="in 2021",
            coarse_value="2021",
            temporal_nature="COARSE_YEAR_ERA",
        ),
    )
    signals = generate_retrieval_signals(rep)
    assert signals.temporal_interval is not None
    assert signals.temporal_interval["coarse_year"] == 2021
    assert "2021-01-01" in signals.temporal_interval["start_date"]
    assert "2021-12-31" in signals.temporal_interval["end_date"]


def test_unit_zero_model_isolation_and_no_sentence_transformers():
    """
    [Contract Test]
    Verifies that running Lexical FTS MultiPathRetriever strictly avoids
    importing SentenceTransformer, torch, or transformers into the Python process.
    """
    assert settings.RETRIEVAL_MODE == "lexical_fts"
    assert settings.embedding_selection_status == "lexical_fts_fallback"

    retriever = MultiPathRetriever()
    assert retriever is not None

    # Verify no sentence_transformers, torch, or transformers in sys.modules
    assert "sentence_transformers" not in sys.modules
    assert "torch" not in sys.modules
    assert "transformers" not in sys.modules


def test_unit_embedder_fallback_prohibits_model_loading():
    """
    [Contract Test]
    Verifies that in RETRIEVAL_MODE == 'lexical_fts', LocalEmbedder enters fallback mode
    and actively refuses to load weights or encode vectors, protecting container RAM.
    """
    embedder = LocalEmbedder()
    assert embedder.is_fallback is True
    assert embedder.model_name == "lexical_fts_fallback"

    with pytest.raises(RuntimeError) as exc_model:
        _ = embedder.model
    assert "LocalEmbedder model loading is disabled" in str(exc_model.value)

    with pytest.raises(RuntimeError) as exc_encode:
        embedder.encode("test text")
    assert "Vector encoding is disabled in lexical FTS fallback mode" in str(exc_encode.value)


def test_unit_empty_query_deterministic_response():
    """
    [Unit Test]
    Verifies that an empty memory representation returns a clean 0-result response
    without attempting database access or crashing.
    """
    rep = V2MemoryRepresentation(raw_input="")
    retriever = MultiPathRetriever()
    response = asyncio.run(retriever.retrieve(rep))

    assert isinstance(response, DiscoveryResponse)
    assert response.candidate_pool_size == 0
    assert response.results == []
    assert "EMPTY_QUERY" in response.coverage_status
    assert response.controlled_recovery_triggered is False


def test_unit_discovery_response_contract_and_serialization():
    """
    [Contract Test]
    Verifies that DiscoveryResponse and CandidateResult conform exactly to Section 18.2 schema
    and serialize cleanly to dict and JSON with extra='forbid' validation.
    """
    result = CandidateResult(
        candidate_id="chunk-uuid-1",
        chunk_id="chunk-uuid-1",
        case_id="case-uuid-1",
        chunk_type="RAW_QUOTE",
        content="User complained about photos disappearing after sync.",
        rank=1,
        score=2.35,
        score_breakdown=ScoreBreakdown(
            base_rrf=0.85,
            bound_bonus=1.5,
            distractor_penalty=0.0,
        ),
        retrieval_paths=["lexical_fts"],
        metadata={"methodology": "UNSOLICITED_PUBLIC", "rating": 1},
    )

    response = DiscoveryResponse(
        raw_input="photos disappearing after sync",
        v2_frame={"raw_input": "photos disappearing after sync"},
        retrieval_signals={"search_query_terms": ["photos", "disappearing", "sync"]},
        coverage_status="COVERAGE_SUFFICIENT",
        controlled_recovery_triggered=False,
        candidate_pool_size=1,
        results=[result],
    )

    # Test serialization
    dumped_dict = response.model_dump()
    assert dumped_dict["candidate_pool_size"] == 1
    assert dumped_dict["results"][0]["score_breakdown"]["bound_bonus"] == 1.5

    dumped_json = response.model_dump_json()
    assert "photos disappearing after sync" in dumped_json
    assert "lexical_fts" in dumped_json


# =============================================================================
# II. LIVE POSTGRESQL / SUPABASE TESTS (Exercises Actual PostgreSQL tsvector/GIN)
# =============================================================================

def test_live_postgres_fts_core_retrieval():
    """
    [Live PostgreSQL / Supabase Test]
    Executes a real PostgreSQL Lexical FTS query against evidence_chunks.search_vector
    using websearch_to_tsquery and idx_chunks_fts on Supabase PostgreSQL 17.
    """
    rep = V2MemoryRepresentation(
        raw_input="wedding photo with cousin",
        events=EventConcept(event_name="wedding"),
        people=[PersonConcept(role="cousin")],
    )
    retriever = MultiPathRetriever()
    response = asyncio.run(retriever.retrieve(rep, top_k=5))

    assert isinstance(response, DiscoveryResponse)
    assert response.candidate_pool_size > 0
    assert len(response.results) <= 5
    assert response.results[0].rank == 1
    assert response.results[0].retrieval_paths == ["lexical_fts"]
    assert response.results[0].score_breakdown.base_rrf > 0.0

    # Content verification: candidate rows must contain query terms
    found_term = False
    for res in response.results:
        content_lower = res.content.lower()
        if "wedding" in content_lower or "cousin" in content_lower:
            found_term = True
            break
    assert found_term, "Retrieved candidates must contain search term matching lexical tsquery"


def test_live_postgres_nonsense_no_match_query():
    """
    [Live PostgreSQL / Supabase Test]
    Verifies that a query with zero matching tsvectors executes on PostgreSQL and
    returns a deterministic empty result without database errors.
    """
    rep = V2MemoryRepresentation(
        raw_input="xyzunobtainium789nonexistent123",
        objects=[ObjectConcept(name="xyzunobtainium789nonexistent123")],
    )
    retriever = MultiPathRetriever()
    response = asyncio.run(retriever.retrieve(rep))

    assert isinstance(response, DiscoveryResponse)
    assert response.candidate_pool_size == 0
    assert response.results == []


def test_live_postgres_structured_filtering_methodology():
    """
    [Live PostgreSQL / Supabase Test]
    Verifies that structured filter methodology='PROMPTED_INTERVIEW' restricts
    candidate cases strictly to interview methodologies in live PostgreSQL.
    """
    rep = V2MemoryRepresentation(
        raw_input="photo search failure",
        objects=[ObjectConcept(name="photo")],
    )
    retriever = MultiPathRetriever()

    filt = RetrievalFilter(methodology="PROMPTED_INTERVIEW")
    response = asyncio.run(retriever.retrieve(rep, filters=filt, top_k=10))

    assert response.candidate_pool_size > 0
    for res in response.results:
        assert res.metadata["methodology"] == "PROMPTED_INTERVIEW"


def test_live_postgres_structured_filtering_rating():
    """
    [Live PostgreSQL / Supabase Test]
    Verifies that structured filter rating=1 restricts candidates to 1-star reviews in live PostgreSQL.
    """
    rep = V2MemoryRepresentation(
        raw_input="google photos update search",
        objects=[ObjectConcept(name="photos")],
    )
    retriever = MultiPathRetriever()

    filt = RetrievalFilter(rating=1)
    response = asyncio.run(retriever.retrieve(rep, filters=filt, top_k=10))

    assert response.candidate_pool_size > 0
    for res in response.results:
        assert res.metadata["rating"] == 1


def test_live_postgres_structured_filtering_category_tags():
    """
    [Live PostgreSQL / Supabase Test]
    Verifies that structured filter category_tags=['SEARCH_ACCURACY'] utilizes PostgreSQL
    array overlap (&&) to return matching cases from live Supabase.
    """
    rep = V2MemoryRepresentation(
        raw_input="photos search",
        objects=[ObjectConcept(name="photos")],
    )
    retriever = MultiPathRetriever()

    filt = RetrievalFilter(category_tags=["SEARCH_ACCURACY"])
    response = asyncio.run(retriever.retrieve(rep, filters=filt, top_k=5))

    assert response.candidate_pool_size > 0
    for res in response.results:
        assert "SEARCH_ACCURACY" in res.metadata.get("category_tags", [])


def test_live_postgres_temporal_filtering_date_boundaries():
    """
    [Live PostgreSQL / Supabase Test]
    Verifies that temporal filters restrict results to the specified creation window in live PostgreSQL.
    """
    rep = V2MemoryRepresentation(
        raw_input="backup and search issues",
        objects=[ObjectConcept(name="backup")],
    )
    retriever = MultiPathRetriever()

    # Broad filter from 2020 to 2027 should return rows
    filt_wide = RetrievalFilter(
        start_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2027, 1, 1, tzinfo=timezone.utc),
    )
    resp_wide = asyncio.run(retriever.retrieve(rep, filters=filt_wide, top_k=5))
    assert resp_wide.candidate_pool_size > 0

    # Narrow filter in the distant future must return 0 rows
    filt_future = RetrievalFilter(
        start_date=datetime(2035, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2036, 1, 1, tzinfo=timezone.utc),
    )
    resp_future = asyncio.run(retriever.retrieve(rep, filters=filt_future, top_k=5))
    assert resp_future.candidate_pool_size == 0
    assert resp_future.results == []


def test_live_postgres_compositional_bound_attribute_bonus():
    """
    [Live PostgreSQL / Supabase Test]
    Verifies that Stage 5 Compositional Matching awards a +1.5 bound bonus
    when candidate text contains both entity and bound attribute in live PostgreSQL.
    """
    rep = V2MemoryRepresentation(
        raw_input="brother on white motorcycle",
        objects=[ObjectConcept(name="motorcycle", attributes=["white"])],
        people=[PersonConcept(role="brother")],
    )
    retriever = MultiPathRetriever()
    response = asyncio.run(retriever.retrieve(rep, top_k=5))

    assert response.candidate_pool_size > 0
    top = response.results[0]
    if "white" in top.content.lower() and "motorcycle" in top.content.lower():
        assert top.score_breakdown.bound_bonus == 1.5
        assert top.score >= 1.5


def test_live_postgres_controlled_recovery_broadening():
    """
    [Live PostgreSQL / Supabase Test]
    Verifies that when a multi-word conjunction yields 0 candidates on strict AND,
    the Controlled Recovery broadening executes, recovering candidates via OR tsquery,
    and sets controlled_recovery_triggered=True.
    """
    # 'motorcycle' exists in corpus, 'diya' exists in corpus, but no chunk has BOTH
    rep = V2MemoryRepresentation(
        raw_input="motorcycle diya",
        objects=[ObjectConcept(name="motorcycle"), ObjectConcept(name="diya")],
    )
    retriever = MultiPathRetriever()
    response = asyncio.run(retriever.retrieve(rep, top_k=5))

    assert response.controlled_recovery_triggered is True
    assert response.candidate_pool_size > 0
    assert len(response.results) > 0
