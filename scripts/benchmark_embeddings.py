"""
Embedding Deployment Benchmark Script (Step 5).

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 9.1, 9.2, 21, 23)
- config/ingestion_manifest.json

Empirically benchmarks the two approved 384-dimensional multilingual candidates:
1. Candidate A: intfloat/multilingual-e5-small (Initial Benchmark Candidate)
2. Candidate B: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (Fallback Contender)

Disqualified models (all-MiniLM-L6-v2, bge-small-en-v1.5, bge-m3) are strictly rejected.

Evaluates against the three governing deployment criteria:
1. Container Memory Headroom: Peak RSS under 5 concurrent requests <= 750 MB.
2. Single-Passage Inference Latency: p95 latency on shared CPU <= 350 ms.
3. Hinglish / Vernacular Retrieval: Cosine similarity ranking on canonical code-mixed pairs.

Outputs:
- benchmark_results.json (machine-readable)
- Console comparison table & evaluation report
"""

import os
import sys
import time
import json
import argparse
import platform
import logging
import threading
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
import numpy as np

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.embedding.embedder import (
    SPEC_APPROVED_CANDIDATES,
    DISQUALIFIED_MODELS,
    INITIAL_BENCHMARK_CANDIDATE,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("benchmark_embeddings")

# Hard Governing Constraints (Spec Section 9.2)
MEMORY_THRESHOLD_MB = 750.0
LATENCY_P95_THRESHOLD_MS = 350.0
CONCURRENCY_WORKERS = 5
WARMUP_RUNS = 5
LATENCY_SAMPLES = 30

# Representative Hinglish Test Pairs (Spec Section 9.2 & Canonical Operating Traces)
HINGLISH_BENCHMARK_PAIRS = [
    {
        "case_id": "case_rohtang_ice",
        "query": "rohtang ki ice",
        "target": "photo of snow mountain and ice glacier in Himalayas rohtang pass",
        "distractors": [
            "photo of sunny beach with palm trees and ocean waves in goa",
            "family gathering portrait at sister wedding haldi ceremony",
            "official insurance bill document receipt pdf",
            "young girl riding a red bicycle on street",
        ],
    },
    {
        "case_id": "case_durga_maid",
        "query": "durga ke sath picture jo meri maid hai",
        "target": "picture with domestic helper maid durga during home cleaning",
        "distractors": [
            "white motorcycle parked near mountain road",
            "group of 5 sisters sitting on sofa living room",
            "yellow truck driving on highway",
            "colleague farewell lunch celebration at office",
        ],
    },
]


def detect_environment() -> Dict[str, Any]:
    """Detects whether running on Railway production container or local machine."""
    is_railway = bool(
        os.getenv("RAILWAY_ENVIRONMENT")
        or os.getenv("RAILWAY_PROJECT_ID")
        or os.getenv("RAILWAY_SERVICE_ID")
    )
    env_name = "Railway Production Container" if is_railway else f"Local Host ({platform.system()} {platform.release()})"
    return {
        "is_railway": is_railway,
        "environment_name": env_name,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count() or 1,
    }


def get_current_rss_mb() -> float:
    """Returns process Resident Set Size (RSS) in megabytes cross-platform."""
    # 1. Linux /proc/self/status (Railway / Docker container)
    try:
        with open("/proc/self/status", "r") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return float(line.split()[1]) / 1024.0  # kB to MB
    except (FileNotFoundError, PermissionError):
        pass

    # 2. Windows psapi GetProcessMemoryInfo
    try:
        import ctypes
        from ctypes import wintypes
        psapi = ctypes.WinDLL("psapi")
        kernel32 = ctypes.WinDLL("kernel32")

        class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t),
            ]

        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(PROCESS_MEMORY_COUNTERS_EX),
            wintypes.DWORD,
        ]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE

        counters = PROCESS_MEMORY_COUNTERS_EX()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS_EX)
        handle = kernel32.GetCurrentProcess()
        if psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            return counters.WorkingSetSize / (1024.0 * 1024.0)
    except Exception:
        pass

    # 3. POSIX fallback
    try:
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform == "darwin":
            return usage / (1024.0 * 1024.0)
        return usage / 1024.0
    except ImportError:
        pass

    return 0.0


def compute_cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Computes standard cosine similarity between two float vectors."""
    a = np.array(vec_a, dtype=np.float32)
    b = np.array(vec_b, dtype=np.float32)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def format_model_query(model_name: str, query: str) -> str:
    """Formats query input with e5 instruction prefix if applicable."""
    if "e5" in model_name.lower():
        return f"query: {query}"
    return query


def format_model_passage(model_name: str, passage: str) -> str:
    """Formats passage input with e5 instruction prefix if applicable."""
    if "e5" in model_name.lower():
        return f"passage: {passage}"
    return passage


class ContinuousMemoryTracker:
    """Background thread polling process RSS to capture peak memory accurately."""
    def __init__(self, interval_sec: float = 0.01):
        self.interval = interval_sec
        self.peak_rss_mb = 0.0
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        self._running = True
        self.peak_rss_mb = get_current_rss_mb()
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()

    def _poll(self):
        while self._running:
            current = get_current_rss_mb()
            if current > self.peak_rss_mb:
                self.peak_rss_mb = current
            time.sleep(self.interval)

    def stop(self) -> float:
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
        current = get_current_rss_mb()
        if current > self.peak_rss_mb:
            self.peak_rss_mb = current
        return self.peak_rss_mb


def benchmark_single_candidate(
    model_name: str,
    max_ram_mb: float = MEMORY_THRESHOLD_MB,
    latency_threshold_ms: float = LATENCY_P95_THRESHOLD_MS,
    concurrency_workers: int = CONCURRENCY_WORKERS,
    warmup_count: int = WARMUP_RUNS,
    sample_count: int = LATENCY_SAMPLES,
) -> Dict[str, Any]:
    """
    Executes the empirical benchmark on a single candidate model.
    Validates memory, latency, and Hinglish retrieval.
    """
    # 1. Candidate validation
    if model_name in DISQUALIFIED_MODELS:
        raise ValueError(f"Model '{model_name}' is DISQUALIFIED by spec Section 9.1.")
    if model_name not in SPEC_APPROVED_CANDIDATES:
        raise ValueError(f"Model '{model_name}' is not in SPEC_APPROVED_CANDIDATES {SPEC_APPROVED_CANDIDATES}.")

    logger.info(f"============================================================")
    logger.info(f"STARTING BENCHMARK: {model_name}")
    logger.info(f"============================================================")

    # A. Memory Baseline
    baseline_rss_mb = get_current_rss_mb()
    logger.info(f"Baseline Process RSS: {baseline_rss_mb:.2f} MB")

    # Load Model (on CPU)
    from sentence_transformers import SentenceTransformer
    load_start = time.perf_counter()
    model = SentenceTransformer(model_name, device="cpu")
    load_time_sec = time.perf_counter() - load_start

    loaded_rss_mb = get_current_rss_mb()
    model_ram_mb = loaded_rss_mb - baseline_rss_mb
    logger.info(f"Model loaded in {load_time_sec:.2f}s. Loaded RSS: {loaded_rss_mb:.2f} MB (Delta: +{model_ram_mb:.2f} MB)")

    # Verify vector dimension
    test_vec = model.encode("test passage", convert_to_numpy=True)
    dim = len(test_vec)
    if dim != 384:
        raise ValueError(f"Model '{model_name}' produced {dim} dimensions; spec requires VECTOR(384).")
    logger.info(f"Vector Dimension Confirmed: {dim} (Complies with PostgreSQL VECTOR(384))")

    # B. Concurrency & Peak Memory Test (5 concurrent requests)
    logger.info(f"Running concurrency memory stress test ({concurrency_workers} concurrent threads)...")
    tracker = ContinuousMemoryTracker(interval_sec=0.005)
    tracker.start()

    stress_texts = [
        "rohtang ki ice wali photo with snowy mountain background",
        "family wedding celebration in 2021 haldi ceremony photo",
        "durga ke sath picture jo meri maid hai in living room",
        "white bike parked near office building around 4 years ago",
        "official document certificate boarding pass Progressive receipt",
    ]

    def _worker_task(worker_id: int):
        for _ in range(10):
            text = stress_texts[worker_id % len(stress_texts)]
            _ = model.encode(text, convert_to_numpy=True)

    threads = []
    for wid in range(concurrency_workers):
        t = threading.Thread(target=_worker_task, args=(wid,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    peak_rss_mb = tracker.stop()
    mem_delta_mb = peak_rss_mb - baseline_rss_mb
    mem_pass = peak_rss_mb <= max_ram_mb

    logger.info(
        f"Memory Stress Test Complete: Peak RSS={peak_rss_mb:.2f} MB (Limit: {max_ram_mb} MB) -> "
        f"{'PASS' if mem_pass else 'FAIL'}"
    )

    # C. Inference Latency Test
    logger.info(f"Running inference latency evaluation ({warmup_count} warmup runs, {sample_count} timed samples)...")
    # Warm-up runs
    for i in range(warmup_count):
        _ = model.encode(f"warmup query {i}", convert_to_numpy=True)

    latencies_ms: List[float] = []
    passage_template = "User remembers photo taken during vacation in Rohtang mountain ice snow trip"
    for i in range(sample_count):
        text = f"{passage_template} sample iteration index {i}"
        t0 = time.perf_counter()
        _ = model.encode(text, convert_to_numpy=True)
        t1 = time.perf_counter()
        latencies_ms.append((t1 - t0) * 1000.0)

    p50_ms = float(np.percentile(latencies_ms, 50))
    p95_ms = float(np.percentile(latencies_ms, 95))
    p99_ms = float(np.percentile(latencies_ms, 99))
    min_ms = float(np.min(latencies_ms))
    max_ms = float(np.max(latencies_ms))
    mean_ms = float(np.mean(latencies_ms))
    latency_pass = p95_ms <= latency_threshold_ms

    logger.info(
        f"Latency Profiling Complete: p50={p50_ms:.1f}ms, p95={p95_ms:.1f}ms, "
        f"p99={p99_ms:.1f}ms, max={max_ms:.1f}ms (Limit: {latency_threshold_ms}ms) -> "
        f"{'PASS' if latency_pass else 'FAIL'}"
    )

    # D. Hinglish / Vernacular Retrieval Ranking Test
    logger.info("Evaluating Hinglish / Vernacular cosine similarity retrieval ranking...")
    retrieval_results = []
    all_retrieval_passed = True

    for pair in HINGLISH_BENCHMARK_PAIRS:
        case_id = pair["case_id"]
        query_text = format_model_query(model_name, pair["query"])
        target_text = format_model_passage(model_name, pair["target"])
        distractor_texts = [format_model_passage(model_name, d) for d in pair["distractors"]]

        q_vec = model.encode(query_text, convert_to_numpy=True).tolist()
        t_vec = model.encode(target_text, convert_to_numpy=True).tolist()
        target_sim = compute_cosine_similarity(q_vec, t_vec)

        # Distractor similarities
        scored_candidates = [(target_sim, "TARGET", pair["target"])]
        for d in distractor_texts:
            d_vec = model.encode(d, convert_to_numpy=True).tolist()
            d_sim = compute_cosine_similarity(q_vec, d_vec)
            scored_candidates.append((d_sim, "DISTRACTOR", d))

        # Rank candidates descending by cosine similarity
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        target_rank = next(idx + 1 for idx, (_, ctype, _) in enumerate(scored_candidates) if ctype == "TARGET")
        pair_success = (target_rank == 1)
        if not pair_success:
            all_retrieval_passed = False

        retrieval_results.append({
            "case_id": case_id,
            "query": pair["query"],
            "target": pair["target"],
            "similarity_score": round(target_sim, 4),
            "rank": target_rank,
            "top_competing_score": round(scored_candidates[1][0], 4) if len(scored_candidates) > 1 else 0.0,
            "margin": round(target_sim - (scored_candidates[1][0] if target_rank == 1 else scored_candidates[0][0]), 4),
            "success": pair_success,
        })

        logger.info(
            f"Case '{case_id}': Query='{pair['query']}' -> Target Rank={target_rank} "
            f"(Sim={target_sim:.4f}) -> {'PASS' if pair_success else 'FAIL'}"
        )

    overall_pass = mem_pass and latency_pass and all_retrieval_passed

    return {
        "model_name": model_name,
        "model_dimension": dim,
        "load_time_sec": round(load_time_sec, 2),
        "memory_metrics": {
            "baseline_rss_mb": round(baseline_rss_mb, 2),
            "loaded_rss_mb": round(loaded_rss_mb, 2),
            "peak_rss_mb": round(peak_rss_mb, 2),
            "memory_delta_mb": round(mem_delta_mb, 2),
            "concurrency_level": concurrency_workers,
            "threshold_mb": max_ram_mb,
            "passed": mem_pass,
        },
        "latency_metrics": {
            "sample_count": sample_count,
            "warmup_runs": warmup_count,
            "p50_ms": round(p50_ms, 2),
            "p95_ms": round(p95_ms, 2),
            "p99_ms": round(p99_ms, 2),
            "min_ms": round(min_ms, 2),
            "max_ms": round(max_ms, 2),
            "mean_ms": round(mean_ms, 2),
            "threshold_ms": latency_threshold_ms,
            "passed": latency_pass,
        },
        "retrieval_metrics": {
            "cases_evaluated": len(retrieval_results),
            "cases_passed": sum(1 for r in retrieval_results if r["success"]),
            "all_passed": all_retrieval_passed,
            "evaluations": retrieval_results,
        },
        "threshold_results": {
            "memory_check": mem_pass,
            "latency_check": latency_pass,
            "retrieval_check": all_retrieval_passed,
            "overall_status": "PASS" if overall_pass else "FAIL",
        },
    }


def execute_full_benchmark(
    candidates: Optional[List[str]] = None,
    output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Runs benchmark for all approved candidates, compares results, and exports report."""
    candidates_to_run = candidates or SPEC_APPROVED_CANDIDATES
    env_info = detect_environment()

    logger.info(f"Target Environment: {env_info['environment_name']}")
    logger.info(f"Platform: {env_info['platform']} | CPUs: {env_info['cpu_count']}")

    candidate_results: Dict[str, Any] = {}
    for cand in candidates_to_run:
        result = benchmark_single_candidate(cand)
        candidate_results[cand] = result

    # Transparent comparative selection logic
    decision = evaluate_selection(candidate_results)

    final_payload = {
        "benchmark_metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "environment": env_info,
            "concurrency_level": CONCURRENCY_WORKERS,
            "memory_threshold_mb": MEMORY_THRESHOLD_MB,
            "latency_p95_threshold_ms": LATENCY_P95_THRESHOLD_MS,
        },
        "candidates": candidate_results,
        "selection_decision": decision,
    }

    # Save machine-readable output
    out_file = output_path or (PROJECT_ROOT / "benchmark_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(final_payload, f, indent=2)
    logger.info(f"Saved benchmark results to {out_file}")

    return final_payload


def evaluate_selection(candidate_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates candidate results strictly against governing criteria:
    A. Memory <= 750 MB
    B. p95 latency <= 350 ms
    C. Hinglish retrieval quality (margin & rank)
    """
    eligible = []
    for name, res in candidate_results.items():
        th = res["threshold_results"]
        if th["overall_status"] == "PASS":
            eligible.append((name, res))

    if not eligible:
        return {
            "selected_model": None,
            "status": "NO_ELIGIBLE_CANDIDATE",
            "reason": "Neither candidate satisfied all hard deployment constraints.",
        }

    if len(eligible) == 1:
        winner_name, winner_res = eligible[0]
        return {
            "selected_model": winner_name,
            "status": "UNCONTESTED_WINNER",
            "reason": f"Only {winner_name} satisfied all three hard deployment constraints.",
            "metrics": {
                "peak_ram_mb": winner_res["memory_metrics"]["peak_rss_mb"],
                "p95_latency_ms": winner_res["latency_metrics"]["p95_ms"],
            },
        }

    # Both passed hard constraints -> compare retrieval margin & MTEB evidence
    # Compare retrieval margins across benchmark test pairs
    cand_margins = {}
    for name, res in eligible:
        avg_margin = float(np.mean([e["margin"] for e in res["retrieval_metrics"]["evaluations"]]))
        cand_margins[name] = avg_margin

    # Rank by retrieval quality margin
    ranked = sorted(eligible, key=lambda x: cand_margins[x[0]], reverse=True)
    winner_name, winner_res = ranked[0]
    runner_up_name, runner_up_res = ranked[1]

    return {
        "selected_model": winner_name,
        "status": "EMPIRICAL_WINNER",
        "reason": (
            f"Both candidates passed hard memory (<=750MB) and latency (<=350ms) thresholds. "
            f"'{winner_name}' selected strictly based on superior empirical vernacular retrieval separation "
            f"(measured average similarity margin: {cand_margins[winner_name]:.4f} vs {cand_margins[runner_up_name]:.4f})."
        ),
        "comparison_summary": {
            winner_name: {
                "peak_ram_mb": winner_res["memory_metrics"]["peak_rss_mb"],
                "p95_latency_ms": winner_res["latency_metrics"]["p95_ms"],
                "avg_retrieval_margin": round(cand_margins[winner_name], 4),
            },
            runner_up_name: {
                "peak_ram_mb": runner_up_res["memory_metrics"]["peak_rss_mb"],
                "p95_latency_ms": runner_up_res["latency_metrics"]["p95_ms"],
                "avg_retrieval_margin": round(cand_margins[runner_up_name], 4),
            },
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Step 5: Embedding Deployment Benchmark CLI")
    parser.add_argument("--output", type=Path, default=None, help="Path to save benchmark_results.json")
    parser.add_argument("--candidates", nargs="+", default=SPEC_APPROVED_CANDIDATES, help="Candidates to benchmark")
    args = parser.parse_args()

    results = execute_full_benchmark(candidates=args.candidates, output_path=args.output)
    print("\n" + "=" * 60)
    print("STEP 5 BENCHMARK COMPLETE")
    print("Selection Decision:", results["selection_decision"]["selected_model"])
    print("Reason:", results["selection_decision"]["reason"])
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
