"""
Automated Test Suite for Phase 3 — Discovery Engine Benchmark Regression Gate.

Governed strictly by:
- part1_discovery_engine_experimental_spec.md
- part1_discovery_engine_implementation_spec.md (Sections 7, 8, 10–13, 24, 28)
- part1_discovery_engine_architecture_final.md (Stages 2–6)
- part1_experimental_benchmark.json
- part1_experiment_results.json

Formal automated pytest gate verifying:
1. All 8 canonical benchmark cases execute successfully through the current Discovery Engine pipeline.
2. Strategy B Mean Recall == 1.00.
3. Strategy B Mean P@1 >= 0.78.
4. Zero-result failure cases == 0 across all 8 canonical cases.
5. Case 7 multi-session coverage == 10/10 days recovered via controlled recovery.
6. Execution maintains strict parity with established historical findings in part1_experiment_results.json.
7. Exercises the CURRENT implementation in backend/app/retrieval/pipeline.py.
8. Operates with zero embedding models loaded (SentenceTransformer, PyTorch, transformers absent).
9. Operates under RETRIEVAL_MODE="lexical_fts" and lexical_fts_fallback.
"""

import sys
import os
import json
import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import patch
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
from app.representation.models import V2MemoryRepresentation
from app.retrieval.models import DiscoveryResponse, CandidateResult
from app.retrieval.pipeline import DiscoveryEnginePipeline

import run_part1_experiment


# Canonical 8 benchmark cases
CANONICAL_BENCHMARK_CASES = [
    "5 sisters",
    "rohtang ki ice wali photo",
    "white bike",
    "diya at the gate",
    "Progressive",
    "document around 4 years ago",
    "yellow truck",
    "wedding",
]


@pytest.fixture(scope="module")
def executed_benchmark_payload() -> Dict[str, Any]:
    """
    Executes the 8-case benchmark runner deterministically.
    Redirects RESULTS_FILE output to a temporary path to guarantee
    the existing part1_experiment_results.json file is not modified.
    """
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_output_path = tmp.name

    try:
        with patch("run_part1_experiment.RESULTS_FILE", tmp_output_path):
            payload = run_part1_experiment.run_all_cases()
    finally:
        if os.path.exists(tmp_output_path):
            try:
                os.remove(tmp_output_path)
            except OSError:
                pass

    return payload


@pytest.fixture(scope="module")
def historical_experiment_results() -> Dict[str, Any]:
    """Loads the established reference results from part1_experiment_results.json."""
    results_path = PROJECT_ROOT / "part1_experiment_results.json"
    with open(results_path, "r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# 1. PROCESS ISOLATION & RUNTIME CONTRACT VERIFICATION (Gates 8 & 9)
# =============================================================================

def test_benchmark_environment_and_zero_model_contract():
    """
    Verifies Phase 3 gate conditions:
    - RETRIEVAL_MODE == 'lexical_fts'
    - Embedding selection status == 'lexical_fts_fallback'
    - Zero embedding models required or loaded by Discovery Engine pipeline
    - LocalEmbedder strictly blocks model weight allocation and vector encoding
    - Zero neural embedding models in sys.modules when run as target gate
    """
    assert settings.RETRIEVAL_MODE == "lexical_fts"
    assert settings.embedding_selection_status == "lexical_fts_fallback"
    assert not settings.EMBEDDING_MODEL_NAME

    # Verify DiscoveryEngine operates with zero embedding model weights
    from app.embedding.embedder import LocalEmbedder
    embedder = LocalEmbedder()
    assert embedder.is_fallback is True
    with pytest.raises(RuntimeError, match="LocalEmbedder model loading is disabled"):
        _ = embedder.model
    with pytest.raises(RuntimeError, match="Vector encoding is disabled in lexical FTS fallback mode"):
        embedder.encode("test passage")

    # In standalone execution gate, verify zero heavy neural dependencies in process
    is_standalone_gate = any("test_benchmark_regression" in arg for arg in sys.argv)
    if is_standalone_gate:
        assert "sentence_transformers" not in sys.modules
        assert "torch" not in sys.modules
        assert "transformers" not in sys.modules


# =============================================================================
# 2. CURRENT PIPELINE IMPLEMENTATION EXERCISE (Gates 1 & 7)
# =============================================================================

def test_pipeline_exercises_all_8_canonical_cases():
    """
    Exercises the CURRENT DiscoveryEnginePipeline in backend/app/retrieval/pipeline.py
    across all 8 canonical benchmark cases.
    Verifies that raw queries flow through Stage 2 -> 3 -> 4 -> 5 -> 6 and return
    valid DiscoveryResponse objects conforming to the Section 18.2 schema.
    """
    pipeline = DiscoveryEnginePipeline()
    assert pipeline is not None

    for case_query in CANONICAL_BENCHMARK_CASES:
        response = asyncio.run(pipeline.run(case_query, top_k=5))

        # Schema & structural contracts
        assert isinstance(response, DiscoveryResponse)
        assert response.raw_input == case_query
        assert isinstance(response.v2_frame, dict)
        assert isinstance(response.retrieval_signals, dict)
        assert response.candidate_pool_size >= 0
        assert isinstance(response.results, list)

        # Ranked ordering validation
        for rank_idx, candidate in enumerate(response.results):
            assert isinstance(candidate, CandidateResult)
            assert candidate.rank == rank_idx + 1
            if rank_idx > 0:
                assert response.results[rank_idx - 1].score >= candidate.score


def test_pipeline_v2_representation_passthrough():
    """
    Verifies that passing a pre-parsed V2MemoryRepresentation directly into
    DiscoveryEnginePipeline.run() preserves the representation without re-parsing.
    """
    pipeline = DiscoveryEnginePipeline()
    v2_rep = V2MemoryRepresentation(
        raw_input="white bike",
        objects=[{"name": "bike", "attributes": ["white"]}],
    )

    response = asyncio.run(pipeline.run(v2_rep, top_k=5))
    assert isinstance(response, DiscoveryResponse)
    assert response.raw_input == "white bike"
    objects = response.v2_frame.get("objects", [])
    assert len(objects) == 1
    assert objects[0]["name"] == "bike"
    assert objects[0]["attributes"] == ["white"]


# =============================================================================
# 3. BENCHMARK METRICS & ACCEPTANCE CRITERIA (Gates 2, 3, 4, 5)
# =============================================================================

def test_strategy_b_mean_target_recall(executed_benchmark_payload: Dict[str, Any]):
    """
    Verifies Phase 3 Gate 2:
    Strategy B Mean Recall across all 8 canonical cases must equal 1.000.
    """
    agg = executed_benchmark_payload["aggregate_metrics"]
    mean_recall = agg["strategy_b_mean_target_recall"]

    assert mean_recall == 1.0, f"Strategy B Mean Recall expected 1.0, got {mean_recall}"
    assert pytest.approx(mean_recall, abs=1e-3) == 1.000

    # Verify per-case recall
    cases = executed_benchmark_payload["cases"]
    assert len(cases) == 8
    for case in cases:
        b_metrics = case["metrics"]["strategy_b"]
        assert b_metrics["target_recall"] == 1.0, (
            f"Case '{case['case_name']}' failed recall: {b_metrics['target_recall']}"
        )


def test_strategy_b_mean_precision_at_1(executed_benchmark_payload: Dict[str, Any]):
    """
    Verifies Phase 3 Gate 3:
    Strategy B Mean P@1 (tie-adjusted) must be >= 0.78 (measured 0.781).
    """
    agg = executed_benchmark_payload["aggregate_metrics"]
    mean_p1 = agg["strategy_b_mean_precision_at_1_tie_adjusted"]

    assert mean_p1 >= 0.78, f"Strategy B Mean P@1 breached threshold: {mean_p1} < 0.78"
    assert pytest.approx(mean_p1, abs=1e-3) == 0.781


def test_zero_result_failures(executed_benchmark_payload: Dict[str, Any]):
    """
    Verifies Phase 3 Gate 4:
    Zero-result failure cases == 0 under Strategy B.
    Every canonical case must recover its designated ground-truth target photo(s).
    """
    cases = executed_benchmark_payload["cases"]
    zero_result_failures = 0

    for case in cases:
        b_metrics = case["metrics"]["strategy_b"]
        targets_recovered = b_metrics["targets_recovered"]
        final_candidate_count = len(case["strategy_b_discovery_engine"]["final_candidate_ids"])

        if targets_recovered == 0 or final_candidate_count == 0:
            zero_result_failures += 1

    assert zero_result_failures == 0, (
        f"Detected {zero_result_failures} zero-result failure cases under Strategy B"
    )


def test_case_7_multi_session_coverage(executed_benchmark_payload: Dict[str, Any]):
    """
    Verifies Phase 3 Gate 5:
    Case 7 multi-session coverage == 10/10 days.
    Tests the coverage check detection of temporal clustering and the controlled
    recovery broadening across the June 2024 utility truck project span.
    """
    case7 = next(c for c in executed_benchmark_payload["cases"] if c["case_name"] == "yellow truck")
    engine_data = case7["strategy_b_discovery_engine"]

    # 1. Coverage Check detected concentration
    assert engine_data["coverage_check"]["decision"] == "INSUFFICIENT"
    assert "concentrated in only 2 initial sessions" in engine_data["coverage_check"]["diagnostic_reason"]

    # 2. Controlled Recovery activated
    assert "timeline broadening" in engine_data["recovery_action"]
    assert len(engine_data["recovered_candidate_ids"]) == 8

    # 3. 10/10 target days recovered
    c7_metrics = case7["metrics"]["strategy_b"]
    assert c7_metrics["targets_recovered"] == 10
    assert c7_metrics["total_targets"] == 10
    assert c7_metrics["target_recall"] == 1.0


# =============================================================================
# 4. HISTORICAL PARITY VERIFICATION (Gate 6)
# =============================================================================

def test_historical_parity_with_established_findings(
    executed_benchmark_payload: Dict[str, Any],
    historical_experiment_results: Dict[str, Any],
):
    """
    Verifies Phase 3 Gate 6:
    Results maintain strict 100% parity with established historical findings in
    part1_experiment_results.json across aggregate metrics and individual case evaluations.
    """
    exec_agg = executed_benchmark_payload["aggregate_metrics"]
    hist_agg = historical_experiment_results["aggregate_metrics"]

    # Aggregate metric parity
    assert exec_agg["strategy_a_mean_target_recall"] == hist_agg["strategy_a_mean_target_recall"]
    assert exec_agg["strategy_b_mean_target_recall"] == hist_agg["strategy_b_mean_target_recall"]
    assert exec_agg["strategy_a_mean_precision_at_1_tie_adjusted"] == hist_agg["strategy_a_mean_precision_at_1_tie_adjusted"]
    assert exec_agg["strategy_b_mean_precision_at_1_tie_adjusted"] == hist_agg["strategy_b_mean_precision_at_1_tie_adjusted"]

    # Per-case parity
    exec_cases = {c["case_name"]: c for c in executed_benchmark_payload["cases"]}
    hist_cases = {c["case_name"]: c for c in historical_experiment_results["cases"]}

    assert set(exec_cases.keys()) == set(hist_cases.keys())

    for case_name, exec_c in exec_cases.items():
        hist_c = hist_cases[case_name]

        # Verify Strategy A metrics parity
        assert exec_c["metrics"]["strategy_a"] == hist_c["metrics"]["strategy_a"], (
            f"Strategy A metric divergence in '{case_name}'"
        )

        # Verify Strategy B metrics parity
        assert exec_c["metrics"]["strategy_b"] == hist_c["metrics"]["strategy_b"], (
            f"Strategy B metric divergence in '{case_name}'"
        )

        # Verify top candidate identity parity
        exec_top = exec_c["strategy_b_discovery_engine"]["candidate_evaluations"][0]["photo_id"]
        hist_top = hist_c["strategy_b_discovery_engine"]["candidate_evaluations"][0]["photo_id"]
        assert exec_top == hist_top, (
            f"Top candidate divergence in '{case_name}': {exec_top} vs {hist_top}"
        )


def test_strategy_b_superiority_over_strategy_a(executed_benchmark_payload: Dict[str, Any]):
    """
    Verifies that Strategy B (Discovery Engine) conclusively outperforms
    Strategy A (Literal Baseline) across all aggregate dimensions:
    - Mean Recall: 1.000 vs 0.650 (+53.8% relative gain)
    - Mean P@1 (Adj): 0.781 vs 0.406 (+92.4% relative gain)
    """
    agg = executed_benchmark_payload["aggregate_metrics"]
    assert agg["strategy_b_mean_target_recall"] > agg["strategy_a_mean_target_recall"]
    assert agg["strategy_b_mean_precision_at_1_tie_adjusted"] > agg["strategy_a_mean_precision_at_1_tie_adjusted"]
