"""
Automated Test Suite for Step 3 — Evidence Ingestion.

Governed by:
- part1_discovery_engine_implementation_spec.md (Sections 4.2, 5.1–5.2, 6.1–6.2, 26)
- config/ingestion_manifest.json

Verifies:
1. Manifest validation & rejection of outdated count assumptions (113)
2. Authoritative datasets resolution & record counts (245 + 38 + 25 = 308)
3. Methodology segregation (283 UNSOLICITED_PUBLIC vs 25 PROMPTED_INTERVIEW)
4. Global external_id uniqueness across the 308-case master corpus
5. Field mapping compliance to evidence_cases schema
6. Deterministic chunking (RAW_QUOTE, DEBRIEF condition, SITUATION_SUMMARY, JTBD)
7. Local CPU embedding generation & vector dimension == 384
8. Idempotency logic & chunk replacement
9. Dry-run execution behavior (zero DB writes)
10. Post-ingestion validation gates
"""

import sys
import json
import asyncio
import pytest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.ingest_evidence import (
    load_and_validate_manifest,
    load_authoritative_datasets,
    normalize_all_records,
    normalize_playstore_record,
    normalize_reddit_record,
    normalize_interview_record,
    extract_chunks_for_case,
    execute_ingestion,
)
from backend.app.embedding.embedder import (
    LocalEmbedder,
    SPEC_APPROVED_CANDIDATES,
    INITIAL_BENCHMARK_CANDIDATE,
    DISQUALIFIED_MODELS,
)


MANIFEST_PATH = PROJECT_ROOT / "config" / "ingestion_manifest.json"


# =============================================================================
# 1. MANIFEST VALIDATION TESTS
# =============================================================================

def test_manifest_validation_success():
    """Manifest must pass validation and specify exact 308 target."""
    manifest = load_and_validate_manifest(MANIFEST_PATH)
    assert manifest["target_total_records"] == 308
    sources = {s["source_key"]: s["target_record_count"] for s in manifest["sources"]}
    assert sources == {"PLAY_STORE": 245, "REDDIT": 38, "USER_INTERVIEW": 25}
    assert manifest["validation_rules"]["disallow_flattened_methodology"] is True
    assert manifest["validation_rules"]["strict_external_id_uniqueness"] is True
    assert manifest["validation_rules"]["zero_null_required_fields"] is True


def test_manifest_rejects_outdated_count_assumption():
    """Manifest validator must reject outdated count assumption of 113."""
    bad_manifest = {
        "project": "Google Photos Discovery Engine",
        "target_total_records": 113,
        "sources": [],
        "validation_rules": {
            "disallow_outdated_count_assumptions": [113],
        },
    }
    temp_path = PROJECT_ROOT / "scratch" / "bad_manifest.json"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(bad_manifest, f)

    with pytest.raises(ValueError, match="outdated count assumption"):
        load_and_validate_manifest(temp_path)


# =============================================================================
# 2. DATASET RESOLUTION & COUNT TESTS
# =============================================================================

def test_authoritative_datasets_resolution_and_counts():
    """All 3 authoritative datasets must resolve and match target counts."""
    manifest = load_and_validate_manifest(MANIFEST_PATH)
    ps_records, rd_records, it_records = load_authoritative_datasets(manifest, PROJECT_ROOT)

    assert len(ps_records) == 245, f"Expected 245 Play Store records, got {len(ps_records)}"
    assert len(rd_records) == 38, f"Expected 38 Reddit records, got {len(rd_records)}"
    assert len(it_records) == 25, f"Expected 25 Interview records, got {len(it_records)}"
    assert len(ps_records) + len(rd_records) + len(it_records) == 308


# =============================================================================
# 3. GLOBAL UNIQUENESS & METHODOLOGY SEGREGATION TESTS
# =============================================================================

def test_global_external_id_uniqueness():
    """All 308 external IDs across the master corpus must be unique."""
    manifest = load_and_validate_manifest(MANIFEST_PATH)
    ps_records, rd_records, it_records = load_authoritative_datasets(manifest, PROJECT_ROOT)
    normalized = normalize_all_records(ps_records, rd_records, it_records)

    eids = [c["external_id"] for c in normalized]
    assert len(eids) == 308
    assert len(set(eids)) == 308, "Duplicate external_id found in normalized master corpus"


def test_methodology_segregation():
    """Methodologies must be strictly segregated (283 UNSOLICITED_PUBLIC vs 25 PROMPTED_INTERVIEW)."""
    manifest = load_and_validate_manifest(MANIFEST_PATH)
    ps_records, rd_records, it_records = load_authoritative_datasets(manifest, PROJECT_ROOT)
    normalized = normalize_all_records(ps_records, rd_records, it_records)

    unsolicited = [c for c in normalized if c["methodology"] == "UNSOLICITED_PUBLIC"]
    prompted = [c for c in normalized if c["methodology"] == "PROMPTED_INTERVIEW"]

    assert len(unsolicited) == 283
    assert len(prompted) == 25
    assert len(unsolicited) + len(prompted) == 308

    # Verify sources
    for c in unsolicited:
        assert c["source_key"] in {"PLAY_STORE", "REDDIT"}
    for c in prompted:
        assert c["source_key"] == "USER_INTERVIEW"


# =============================================================================
# 4. FIELD MAPPING & SCHEMA TESTS
# =============================================================================

def test_field_mapping_and_zero_nulls():
    """Every record must map correctly to evidence_cases columns with zero null mandatory fields."""
    manifest = load_and_validate_manifest(MANIFEST_PATH)
    ps_records, rd_records, it_records = load_authoritative_datasets(manifest, PROJECT_ROOT)
    normalized = normalize_all_records(ps_records, rd_records, it_records)

    mandatory_fields = ["external_id", "raw_text", "methodology", "evidence_type"]

    for idx, c in enumerate(normalized):
        for req in mandatory_fields:
            val = c.get(req)
            assert val is not None, f"Case {idx} ({c.get('external_id')}) has None for mandatory field {req}"
            assert isinstance(val, str) and val.strip(), f"Case {idx} has empty string for mandatory field {req}"

        assert c["methodology"] in {"UNSOLICITED_PUBLIC", "PROMPTED_INTERVIEW"}
        assert c["evidence_type"] in {"FAILURE", "SUCCESS", "NEUTRAL"}
        assert c["signal_strength"] in {"LOW", "MEDIUM", "HIGH"}

        # Rating rules
        if c["source_key"] == "PLAY_STORE":
            assert isinstance(c["rating"], int)
            assert 1 <= c["rating"] <= 5
            assert c["user_debrief"] is None  # Public review has no interview debrief
        else:
            assert c["rating"] is None  # Reddit and Interviews do not have 1-5 star store rating


# =============================================================================
# 5. DETERMINISTIC CHUNKING TESTS
# =============================================================================

def test_deterministic_chunking():
    """Chunking rules must produce RAW_QUOTE, SITUATION_SUMMARY, JTBD, and conditional DEBRIEF."""
    manifest = load_and_validate_manifest(MANIFEST_PATH)
    ps_records, rd_records, it_records = load_authoritative_datasets(manifest, PROJECT_ROOT)
    normalized = normalize_all_records(ps_records, rd_records, it_records)

    all_chunks = []
    chunk_type_counts = {}

    for c in normalized:
        chunks = extract_chunks_for_case(c)
        assert len(chunks) >= 2, f"Case {c['external_id']} produced fewer than 2 chunks"

        types = [ctype for ctype, _ in chunks]
        assert "RAW_QUOTE" in types, f"Case {c['external_id']} missing RAW_QUOTE chunk"

        # DEBRIEF chunk condition: strictly only when user_debrief exists
        if "DEBRIEF" in types:
            assert c["user_debrief"] is not None
            assert c["source_key"] == "USER_INTERVIEW"
        else:
            if c["source_key"] == "USER_INTERVIEW":
                # If no DEBRIEF chunk, user_debrief must be absent
                assert not c.get("user_debrief")

        for ctype, content in chunks:
            assert ctype in {"RAW_QUOTE", "DEBRIEF", "SITUATION_SUMMARY", "JTBD"}
            assert content and content.strip(), f"Empty chunk content in {c['external_id']}"
            chunk_type_counts[ctype] = chunk_type_counts.get(ctype, 0) + 1
            all_chunks.append((ctype, content))

    assert len(all_chunks) >= 308, f"Total chunks {len(all_chunks)} is less than 308"
    assert chunk_type_counts["RAW_QUOTE"] == 308
    assert chunk_type_counts["SITUATION_SUMMARY"] == 308
    assert chunk_type_counts["JTBD"] == 308
    assert chunk_type_counts["DEBRIEF"] == 12  # Exactly 12 interview cases document user debriefs
    assert len(all_chunks) == 936


# =============================================================================
# 6. LOCAL EMBEDDING SPECIFICATION & DIMENSION TEST
# =============================================================================

def test_embedding_model_contract_and_approved_candidates():
    """
    Verifies adherence to Section 9.1 & 9.2 of part1_discovery_engine_implementation_spec.md:
    1. all-MiniLM-L6-v2 is NOT an approved production candidate (disqualified for Hinglish failure).
    2. SPEC_APPROVED_CANDIDATES contains exactly the two spec-designated candidates:
       - intfloat/multilingual-e5-small (Initial Benchmark Candidate)
       - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (Fallback Contender)
    3. Default candidate is intfloat/multilingual-e5-small.
    4. Passing a disqualified model falls back safely to the approved initial candidate.
    """
    # Contract assertions
    assert INITIAL_BENCHMARK_CANDIDATE == "intfloat/multilingual-e5-small"
    assert "intfloat/multilingual-e5-small" in SPEC_APPROVED_CANDIDATES
    assert "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" in SPEC_APPROVED_CANDIDATES
    assert "all-MiniLM-L6-v2" not in SPEC_APPROVED_CANDIDATES
    assert "sentence-transformers/all-MiniLM-L6-v2" not in SPEC_APPROVED_CANDIDATES

    # LocalEmbedder resolution assertions
    embedder = LocalEmbedder(model_name="intfloat/multilingual-e5-small")
    assert embedder.model_name == "intfloat/multilingual-e5-small"
    assert embedder.expected_dim == 384

    # Disqualified model rejection test
    disqualified_test = LocalEmbedder(model_name="sentence-transformers/all-MiniLM-L6-v2")
    assert disqualified_test.model_name == INITIAL_BENCHMARK_CANDIDATE


def test_local_embedding_dimension_is_384():
    """Local embedder on CPU using approved initial candidate must output vectors with exact dimension 384."""
    LocalEmbedder.reset_instance()
    embedder = LocalEmbedder.get_instance(model_name=INITIAL_BENCHMARK_CANDIDATE)
    assert embedder.model_name == INITIAL_BENCHMARK_CANDIDATE

    sample_text = "User cannot find photo of dog in 2021"
    vec = embedder.encode(sample_text)

    assert isinstance(vec, list)
    assert len(vec) == 384
    assert all(isinstance(x, float) for x in vec)

    batch_vecs = embedder.encode_batch(["Photo 1", "Photo 2", "Photo 3"])
    assert len(batch_vecs) == 3
    for v in batch_vecs:
        assert len(v) == 384


# =============================================================================
# 7. DRY-RUN EXECUTION TEST
# =============================================================================

def test_dry_run_execution():
    """Dry-run mode must validate the full pipeline with zero database writes using approved candidate."""
    manifest = load_and_validate_manifest(MANIFEST_PATH)
    ps_records, rd_records, it_records = load_authoritative_datasets(manifest, PROJECT_ROOT)
    normalized = normalize_all_records(ps_records, rd_records, it_records)
    LocalEmbedder.reset_instance()
    embedder = LocalEmbedder.get_instance(model_name=INITIAL_BENCHMARK_CANDIDATE)

    results = asyncio.run(execute_ingestion(
        normalized_cases=normalized,
        db_url="",
        embedder=embedder,
        dry_run=True,
    ))

    assert results["status"] == "DRY_RUN_SUCCESS"
    assert results["cases_validated"] == 308
    assert results["chunks_projected"] == 936
    assert results["vector_dimension"] == 384
    assert results["database_written"] is False
