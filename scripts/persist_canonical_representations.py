"""
Canonical Benchmark Memory Representation Persistence Script (Step 4).

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 4.1, 7.1, 8.2)
- part1_discovery_engine_operating_spec_final.md (Canonical Cases 1–8)

Persists the 8 canonical benchmark queries into the Supabase memory_representations
table idempotently, setting is_benchmark_case=True.

Guarantees:
- Idempotent execution (safe to run repeatedly)
- Zero alterations to evidence_cases, evidence_chunks, or sources
- Full Pydantic V2 schema validation before persistence
"""

import sys
import os
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR / ".env")

import asyncpg
from app.representation.rules import parse_deterministically
from app.representation.persistence import (
    persist_representation,
    fetch_representation_by_id,
    _get_clean_db_url,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("persist_canonical")

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


async def run():
    db_url = _get_clean_db_url()
    logger.info("Connecting to Supabase PostgreSQL...")
    conn = await asyncpg.connect(db_url, statement_cache_size=0)

    try:
        # Pre-execution count checks
        pre_cases = await conn.fetchval("SELECT count(*) FROM evidence_cases;")
        pre_chunks = await conn.fetchval("SELECT count(*) FROM evidence_chunks;")
        pre_sources = await conn.fetchval("SELECT count(*) FROM sources;")
        pre_reps = await conn.fetchval("SELECT count(*) FROM memory_representations;")

        logger.info(
            f"Pre-check: sources={pre_sources}, evidence_cases={pre_cases}, "
            f"evidence_chunks={pre_chunks}, memory_representations={pre_reps}"
        )

        persisted_ids = []
        for raw in CANONICAL_BENCHMARK_CASES:
            rep = parse_deterministically(raw)
            # Validate model
            logger.info(f"Interpreting & persisting canonical case: '{raw}'...")
            rep_id = await persist_representation(
                representation=rep,
                conn=conn,
                is_benchmark_case=True,
            )
            persisted_ids.append((raw, rep_id))

        # Re-fetch and validate each persisted representation
        logger.info("Validating persisted rows against Pydantic schema...")
        for raw, rep_id in persisted_ids:
            fetched = await fetch_representation_by_id(rep_id, conn=conn)
            assert fetched is not None, f"Failed to retrieve representation {rep_id}"
            assert fetched.raw_input == raw, f"raw_input mismatch: {fetched.raw_input} != {raw}"
            logger.info(f"Validated '{raw}' (UUID: {rep_id})")

        # Post-execution count checks
        post_cases = await conn.fetchval("SELECT count(*) FROM evidence_cases;")
        post_chunks = await conn.fetchval("SELECT count(*) FROM evidence_chunks;")
        post_sources = await conn.fetchval("SELECT count(*) FROM sources;")
        post_reps = await conn.fetchval("SELECT count(*) FROM memory_representations;")

        logger.info(
            f"Post-check: sources={post_sources}, evidence_cases={post_cases}, "
            f"evidence_chunks={post_chunks}, memory_representations={post_reps}"
        )

        # Integrity assertions
        assert post_cases == pre_cases == 308, f"evidence_cases modified! {pre_cases} -> {post_cases}"
        assert post_chunks == pre_chunks == 936, f"evidence_chunks modified! {pre_chunks} -> {post_chunks}"
        assert post_sources == pre_sources == 3, f"sources modified! {pre_sources} -> {post_sources}"
        assert post_reps == 8, f"Expected 8 memory_representations, found {post_reps}"

        logger.info("ALL INTEGRITY GATES PASSED: 8 canonical benchmark cases persisted safely.")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run())
