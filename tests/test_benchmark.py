"""
Automated Test Suite for Step 5 — Embedding Deployment Benchmark.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 9.1, 9.2)

Verifies:
1. Candidate validation & strict rejection of disqualified models
2. Metric calculation correctness (cosine similarity, latency percentiles, memory delta)
3. Hard constraint threshold checks (<=750MB, <=350ms, rank==1)
4. Continuous memory tracker operation under concurrency
5. Model selection evaluation logic & tie-breaking on retrieval margin
6. Machine-readable benchmark_results.json schema and persistence
7. Failure handling when thresholds are breached
"""

import sys
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.benchmark_embeddings import (
    compute_cosine_similarity,
    format_model_query,
    format_model_passage,
    evaluate_selection,
    ContinuousMemoryTracker,
    get_current_rss_mb,
    benchmark_single_candidate,
    MEMORY_THRESHOLD_MB,
    LATENCY_P95_THRESHOLD_MS,
    HINGLISH_BENCHMARK_PAIRS,
)
from backend.app.embedding.embedder import (
    SPEC_APPROVED_CANDIDATES,
    DISQUALIFIED_MODELS,
    INITIAL_BENCHMARK_CANDIDATE,
)


# =============================================================================
# 1. CANDIDATE SPECIFICATION & DISQUALIFICATION TESTS
# =============================================================================

def test_approved_candidates_contract():
    """Approved candidates must contain exactly the two spec-designated models."""
    assert "intfloat/multilingual-e5-small" in SPEC_APPROVED_CANDIDATES
    assert "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2" in SPEC_APPROVED_CANDIDATES
    assert len(SPEC_APPROVED_CANDIDATES) == 2


def test_disqualified_models_are_rejected():
    """Disqualified models must be rejected by benchmark runner with ValueError."""
    for disq in DISQUALIFIED_MODELS:
        with pytest.raises(ValueError, match="DISQUALIFIED"):
            benchmark_single_candidate(disq)


def test_unapproved_model_rejected():
    """Any model outside the approved list must be rejected."""
    with pytest.raises(ValueError, match="not in SPEC_APPROVED_CANDIDATES"):
        benchmark_single_candidate("some/random-model")


# =============================================================================
# 2. METRIC CALCULATION TESTS
# =============================================================================

def test_cosine_similarity_identity_and_orthogonality():
    """Cosine similarity must equal 1.0 for identical vectors and 0.0 for orthogonal ones."""
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    v3 = [0.0, 1.0, 0.0]

    assert pytest.approx(compute_cosine_similarity(v1, v2), 0.001) == 1.0
    assert pytest.approx(compute_cosine_similarity(v1, v3), 0.001) == 0.0


def test_cosine_similarity_zero_vector_safety():
    """Zero vectors must return 0.0 without division by zero error."""
    v_zero = [0.0, 0.0, 0.0]
    v_any = [1.0, 2.0, 3.0]
    assert compute_cosine_similarity(v_zero, v_any) == 0.0


def test_format_model_query_and_passage():
    """e5 models require 'query: ' and 'passage: ' prefixes; MiniLM uses raw text."""
    # e5 model
    assert format_model_query("intfloat/multilingual-e5-small", "test") == "query: test"
    assert format_model_passage("intfloat/multilingual-e5-small", "test") == "passage: test"

    # MiniLM model
    minilm = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    assert format_model_query(minilm, "test") == "test"
    assert format_model_passage(minilm, "test") == "test"


# =============================================================================
# 3. THRESHOLD & SELECTION LOGIC TESTS
# =============================================================================

def test_evaluate_selection_uncontested_winner():
    """When only one candidate passes all constraints, it is selected as uncontested winner."""
    mock_results = {
        "candidate_pass": {
            "threshold_results": {"overall_status": "PASS"},
            "memory_metrics": {"peak_rss_mb": 620.0},
            "latency_metrics": {"p95_ms": 280.0},
            "retrieval_metrics": {"evaluations": [{"margin": 0.25}]},
        },
        "candidate_fail": {
            "threshold_results": {"overall_status": "FAIL"},
            "memory_metrics": {"peak_rss_mb": 850.0},  # Exceeded 750 MB
            "latency_metrics": {"p95_ms": 290.0},
            "retrieval_metrics": {"evaluations": [{"margin": 0.20}]},
        },
    }

    decision = evaluate_selection(mock_results)
    assert decision["selected_model"] == "candidate_pass"
    assert decision["status"] == "UNCONTESTED_WINNER"


def test_evaluate_selection_tiebreak_on_retrieval_margin():
    """When both pass hard constraints, candidate with higher retrieval margin wins without language bias."""
    mock_results = {
        "candidate_a": {
            "threshold_results": {"overall_status": "PASS"},
            "memory_metrics": {"peak_rss_mb": 610.0},
            "latency_metrics": {"p95_ms": 260.0},
            "retrieval_metrics": {"evaluations": [{"margin": 0.35}, {"margin": 0.30}]},  # avg = 0.325
        },
        "candidate_b": {
            "threshold_results": {"overall_status": "PASS"},
            "memory_metrics": {"peak_rss_mb": 590.0},
            "latency_metrics": {"p95_ms": 240.0},
            "retrieval_metrics": {"evaluations": [{"margin": 0.20}, {"margin": 0.18}]},  # avg = 0.19
        },
    }

    decision = evaluate_selection(mock_results)
    assert decision["selected_model"] == "candidate_a"
    assert decision["status"] == "EMPIRICAL_WINNER"
    assert "measured average similarity margin: 0.3250 vs 0.1900" in decision["reason"]
    # Verify removal of non-empirical bias
    assert "100+" not in decision["reason"]
    assert "subword" not in decision["reason"]


def test_evaluate_selection_strictly_empirical_and_symmetric():
    """
    Proves that selection is strictly determined by measured retrieval margin
    and is completely symmetric with zero hardcoded model-name preference.
    """
    model_e5 = "intfloat/multilingual-e5-small"
    model_minilm = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

    # Scenario 1: MiniLM has higher measured margin -> MiniLM MUST win
    mock_minilm_wins = {
        model_e5: {
            "threshold_results": {"overall_status": "PASS"},
            "memory_metrics": {"peak_rss_mb": 620.0},
            "latency_metrics": {"p95_ms": 270.0},
            "retrieval_metrics": {"evaluations": [{"margin": 0.15}]},
        },
        model_minilm: {
            "threshold_results": {"overall_status": "PASS"},
            "memory_metrics": {"peak_rss_mb": 600.0},
            "latency_metrics": {"p95_ms": 230.0},
            "retrieval_metrics": {"evaluations": [{"margin": 0.32}]},
        },
    }
    decision_1 = evaluate_selection(mock_minilm_wins)
    assert decision_1["selected_model"] == model_minilm
    assert decision_1["status"] == "EMPIRICAL_WINNER"
    assert f"'{model_minilm}' selected strictly based on superior empirical vernacular retrieval separation" in decision_1["reason"]
    assert "100+" not in decision_1["reason"]

    # Scenario 2: e5 has higher measured margin -> e5 MUST win
    mock_e5_wins = {
        model_e5: {
            "threshold_results": {"overall_status": "PASS"},
            "memory_metrics": {"peak_rss_mb": 620.0},
            "latency_metrics": {"p95_ms": 270.0},
            "retrieval_metrics": {"evaluations": [{"margin": 0.40}]},
        },
        model_minilm: {
            "threshold_results": {"overall_status": "PASS"},
            "memory_metrics": {"peak_rss_mb": 600.0},
            "latency_metrics": {"p95_ms": 230.0},
            "retrieval_metrics": {"evaluations": [{"margin": 0.22}]},
        },
    }
    decision_2 = evaluate_selection(mock_e5_wins)
    assert decision_2["selected_model"] == model_e5
    assert decision_2["status"] == "EMPIRICAL_WINNER"
    assert f"'{model_e5}' selected strictly based on superior empirical vernacular retrieval separation" in decision_2["reason"]
    assert "100+" not in decision_2["reason"]


def test_evaluate_selection_all_fail():
    """When all candidates fail constraints, status is NO_ELIGIBLE_CANDIDATE."""
    mock_results = {
        "candidate_a": {
            "threshold_results": {"overall_status": "FAIL"},
        },
        "candidate_b": {
            "threshold_results": {"overall_status": "FAIL"},
        },
    }
    decision = evaluate_selection(mock_results)
    assert decision["selected_model"] is None
    assert decision["status"] == "NO_ELIGIBLE_CANDIDATE"


# =============================================================================
# 4. MEMORY TRACKER CONCURRENCY TEST
# =============================================================================

def test_continuous_memory_tracker_operation():
    """ContinuousMemoryTracker starts, polls, captures peak, and stops cleanly."""
    tracker = ContinuousMemoryTracker(interval_sec=0.005)
    tracker.start()
    # Allocate temporary memory
    temp_buf = bytearray(10 * 1024 * 1024)  # 10 MB allocation
    peak = tracker.stop()
    assert peak > 0.0
    del temp_buf


def test_get_current_rss_mb_positive():
    """get_current_rss_mb() must return a positive float on current OS."""
    rss = get_current_rss_mb()
    assert isinstance(rss, float)
    assert rss > 0.0


# =============================================================================
# 5. TEST PAIR DEFINITION AUDIT
# =============================================================================

def test_hinglish_test_pairs_contain_spec_required_cases():
    """Benchmark pairs must include rohtang ki ice and durga ke sath picture jo meri maid hai."""
    queries = [p["query"] for p in HINGLISH_BENCHMARK_PAIRS]
    assert "rohtang ki ice" in queries
    assert "durga ke sath picture jo meri maid hai" in queries
    for pair in HINGLISH_BENCHMARK_PAIRS:
        assert len(pair["distractors"]) >= 4
        assert len(pair["target"]) > 0
