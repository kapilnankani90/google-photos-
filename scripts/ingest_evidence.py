"""
Master Evidence Ingestion Pipeline CLI (Step 3).

Authoritative engineering contract: part1_discovery_engine_implementation_spec.md (Section 5)
Governed by: config/ingestion_manifest.json

Target Corpus:
- 245 Google Play Store Cases (UNSOLICITED_PUBLIC)
- 38 Reddit r/googlephotos Cases (UNSOLICITED_PUBLIC)
- 25 1:1 User Interview Retrieval Episodes (PROMPTED_INTERVIEW)
Total: 308 records.

Execution is strictly idempotent.
Supports --dry-run for complete pre-flight validation without database writes.
"""

import os
import sys
import json
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dotenv import load_dotenv

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Load backend/.env
env_path = PROJECT_ROOT / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

from backend.app.embedding.embedder import LocalEmbedder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ingest_evidence")


# =============================================================================
# 1. MANIFEST & PRE-FLIGHT VALIDATION
# =============================================================================

def load_and_validate_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Loads and validates the declarative ingestion manifest."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # 1. Check required top-level keys
    for k in ["project", "target_total_records", "sources", "validation_rules"]:
        if k not in manifest:
            raise ValueError(f"Manifest missing required top-level key: {k}")

    # 2. Check outdated count assumptions rule
    rules = manifest.get("validation_rules", {})
    disallowed_counts = rules.get("disallow_outdated_count_assumptions", [])
    if 113 in disallowed_counts and manifest["target_total_records"] == 113:
        raise ValueError("Manifest violates rule: 113 is an outdated count assumption.")

    if manifest["target_total_records"] != 308:
        raise ValueError(
            f"Manifest target_total_records must be 308, got {manifest['target_total_records']}"
        )

    # 3. Check sources configuration
    sources = manifest.get("sources", [])
    source_keys = {s.get("source_key") for s in sources}
    expected_sources = {"PLAY_STORE", "REDDIT", "USER_INTERVIEW"}
    if source_keys != expected_sources:
        raise ValueError(f"Expected sources {expected_sources}, got {source_keys}")

    # Check targets
    targets = {s["source_key"]: s.get("target_record_count") for s in sources}
    if targets != {"PLAY_STORE": 245, "REDDIT": 38, "USER_INTERVIEW": 25}:
        raise ValueError(f"Invalid target counts in manifest: {targets}")

    logger.info("Manifest pre-flight validation: PASS (Target: 308 records across 3 sources)")
    return manifest


def load_authoritative_datasets(manifest: Dict[str, Any], base_dir: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Resolves and loads the 3 authoritative evidence datasets."""
    sources_map = {s["source_key"]: s for s in manifest["sources"]}

    # 1. Play Store
    ps_conf = sources_map["PLAY_STORE"]
    ps_file = ps_conf.get("authoritative_dataset") or "part1_playstore_evidence_245_authoritative.json"
    ps_path = base_dir / ps_file
    if not ps_path.exists():
        raise FileNotFoundError(f"Authoritative Play Store dataset not found at {ps_path}")
    with open(ps_path, "r", encoding="utf-8") as f:
        ps_json = json.load(f)
        ps_records = ps_json.get("cases", ps_json if isinstance(ps_json, list) else [])

    if len(ps_records) != 245:
        raise ValueError(f"Play Store authoritative dataset must have exactly 245 records, got {len(ps_records)}")

    # 2. Reddit
    rd_conf = sources_map["REDDIT"]
    rd_file = rd_conf.get("authoritative_dataset") or "reddit_evidence_dataset.json"
    rd_path = base_dir / rd_file
    if not rd_path.exists():
        raise FileNotFoundError(f"Authoritative Reddit dataset not found at {rd_path}")
    with open(rd_path, "r", encoding="utf-8") as f:
        rd_records = json.load(f)

    if len(rd_records) != 38:
        raise ValueError(f"Reddit authoritative dataset must have exactly 38 records, got {len(rd_records)}")

    # 3. Interviews
    it_conf = sources_map["USER_INTERVIEW"]
    it_file = it_conf.get("authoritative_dataset") or "interview_evidence_dataset.json"
    it_path = base_dir / it_file
    if not it_path.exists():
        raise FileNotFoundError(f"Authoritative Interview dataset not found at {it_path}")
    with open(it_path, "r", encoding="utf-8") as f:
        it_records = json.load(f)

    if len(it_records) != 25:
        raise ValueError(f"Interview authoritative dataset must have exactly 25 records, got {len(it_records)}")

    logger.info("Authoritative datasets resolved and loaded successfully (245 PS + 38 RD + 25 ITV = 308 Total)")
    return ps_records, rd_records, it_records


# =============================================================================
# 2. NORMALIZATION & MAPPING
# =============================================================================

def normalize_evidence_type(raw_type: Optional[str]) -> str:
    """Enforces database check constraint: evidence_type IN ('FAILURE', 'SUCCESS', 'NEUTRAL')."""
    if not raw_type:
        return "FAILURE"
    val = str(raw_type).strip().upper()
    if val in {"FAILURE", "PAIN_POINT", "ERROR", "BUG"}:
        return "FAILURE"
    if val in {"SUCCESS", "FEATURE_CONFIRMED"}:
        return "SUCCESS"
    if val in {"NEUTRAL", "MIXED", "FEATURE_REQUEST", "EXPECTATION"}:
        return "NEUTRAL"
    return "FAILURE"


def normalize_playstore_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes a Play Store record into the evidence_cases schema."""
    eid = rec["external_id"]
    raw_text = rec["raw_text"]
    rating = rec.get("rating")
    if rating is not None and not (1 <= rating <= 5):
        raise ValueError(f"Invalid rating {rating} in Play Store record {eid}")

    sit_dict = {
        "retrieval_situation": rec.get("retrieval_situation"),
        "retrieval_clue": rec.get("retrieval_clue"),
        "search_method": rec.get("search_method"),
        "outcome": rec.get("outcome"),
        "evidence_category": rec.get("evidence_category"),
        "what_user_remembers": rec.get("what_user_remembers_or_wants_to_find"),
    }

    return {
        "external_id": eid,
        "source_key": "PLAY_STORE",
        "raw_text": raw_text,
        "user_debrief": None,
        "app_version": rec.get("app_version"),
        "rating": rating,
        "methodology": "UNSOLICITED_PUBLIC",
        "evidence_type": normalize_evidence_type(rec.get("evidence_type", "FAILURE")),
        "failure_mode": rec.get("failure_mode"),
        "job_to_be_done": rec.get("job_to_be_done"),
        "signal_strength": rec.get("signal_strength", "MEDIUM"),
        "category_tags": rec.get("category_tags", []),
        "structured_situation": sit_dict,
        "raw_record": rec,
    }


def normalize_reddit_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes a Reddit record into the evidence_cases schema."""
    eid = rec.get("review_id") or rec.get("external_id")
    raw_text = rec.get("original_review") or rec.get("raw_text")

    cat = rec.get("category", [])
    if isinstance(cat, str):
        cat = [cat]

    sit_dict = rec.get("specific_retrieval_situation") or {}
    if not isinstance(sit_dict, dict):
        sit_dict = {"situation_description": str(sit_dict)}
    sit_dict["research_interpretation"] = rec.get("research_interpretation")

    return {
        "external_id": eid,
        "source_key": "REDDIT",
        "raw_text": raw_text,
        "user_debrief": None,
        "app_version": None,
        "rating": None,
        "methodology": "UNSOLICITED_PUBLIC",
        "evidence_type": normalize_evidence_type(rec.get("evidence_type", "FAILURE")),
        "failure_mode": rec.get("failure_mode"),
        "job_to_be_done": rec.get("job_to_be_done"),
        "signal_strength": rec.get("signal_strength", "MEDIUM"),
        "category_tags": cat,
        "structured_situation": sit_dict,
        "raw_record": rec,
    }


def normalize_interview_record(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes a User Interview record into the evidence_cases schema."""
    eid = rec.get("evidence_id") or rec.get("external_id")
    raw_text = rec.get("original_notes") or rec.get("raw_text")
    debrief = rec.get("user_debrief_reflection") or rec.get("user_debrief")

    cat = rec.get("category", [])
    if isinstance(cat, str):
        cat = [cat]

    sit_dict = rec.get("specific_retrieval_situation") or {}
    if not isinstance(sit_dict, dict):
        sit_dict = {"situation_description": str(sit_dict)}
    sit_dict["scenario_id"] = rec.get("scenario_id")
    sit_dict["scenario_title"] = rec.get("scenario_title")
    sit_dict["candidate_id"] = rec.get("candidate_id")
    sit_dict["candidate_name"] = rec.get("candidate_name")
    sit_dict["research_interpretation"] = rec.get("research_interpretation")
    sit_dict["queries_attempted"] = rec.get("queries_attempted")
    sit_dict["outcome"] = rec.get("outcome")

    return {
        "external_id": eid,
        "source_key": "USER_INTERVIEW",
        "raw_text": raw_text,
        "user_debrief": debrief,
        "app_version": None,
        "rating": None,
        "methodology": "PROMPTED_INTERVIEW",
        "evidence_type": normalize_evidence_type(rec.get("evidence_type", "SUCCESS")),
        "failure_mode": rec.get("failure_mode"),
        "job_to_be_done": rec.get("job_to_be_done"),
        "signal_strength": rec.get("signal_strength", "MEDIUM"),
        "category_tags": cat,
        "structured_situation": sit_dict,
        "raw_record": rec,
    }


def normalize_all_records(
    ps_records: List[Dict[str, Any]],
    rd_records: List[Dict[str, Any]],
    it_records: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Normalizes all 308 records and verifies global integrity rules."""
    normalized: List[Dict[str, Any]] = []

    for r in ps_records:
        normalized.append(normalize_playstore_record(r))
    for r in rd_records:
        normalized.append(normalize_reddit_record(r))
    for r in it_records:
        normalized.append(normalize_interview_record(r))

    if len(normalized) != 308:
        raise ValueError(f"Expected 308 normalized cases, got {len(normalized)}")

    # 1. Global external_id uniqueness
    eids = [c["external_id"] for c in normalized]
    if len(eids) != len(set(eids)):
        dupes = [eid for eid in eids if eids.count(eid) > 1]
        raise ValueError(f"Duplicate external_ids detected in master corpus: {set(dupes)}")

    # 2. Zero null mandatory fields
    for idx, c in enumerate(normalized):
        for req in ["external_id", "raw_text", "methodology", "evidence_type"]:
            val = c.get(req)
            if val is None or (isinstance(val, str) and not val.strip()):
                raise ValueError(f"Case {idx} ({c.get('external_id')}) missing mandatory field: {req}")

    # 3. Methodology segregation check
    unsolicited_count = sum(1 for c in normalized if c["methodology"] == "UNSOLICITED_PUBLIC")
    prompted_count = sum(1 for c in normalized if c["methodology"] == "PROMPTED_INTERVIEW")

    if unsolicited_count != 283:
        raise ValueError(f"Expected 283 UNSOLICITED_PUBLIC cases, got {unsolicited_count}")
    if prompted_count != 25:
        raise ValueError(f"Expected 25 PROMPTED_INTERVIEW cases, got {prompted_count}")

    logger.info("Normalization & Global Uniqueness Check: PASS (308 distinct cases, zero missing mandatory fields)")
    return normalized


# =============================================================================
# 3. DETERMINISTIC CHUNKING
# =============================================================================

def extract_chunks_for_case(case: Dict[str, Any]) -> List[Tuple[str, str]]:
    """
    Extracts deterministic chunks for a given case:
    - RAW_QUOTE (always)
    - DEBRIEF (only if user_debrief exists and is non-empty)
    - SITUATION_SUMMARY (if available)
    - JTBD (if available)
    """
    chunks: List[Tuple[str, str]] = []

    # 1. RAW_QUOTE (always present)
    raw = case["raw_text"]
    if raw and raw.strip():
        chunks.append(("RAW_QUOTE", raw.strip()))

    # 2. DEBRIEF (only if non-null and non-empty and not UNKNOWN)
    debrief = case.get("user_debrief")
    if (
        debrief
        and isinstance(debrief, str)
        and debrief.strip()
        and debrief.strip() != "UNKNOWN / NOT_STATED"
    ):
        chunks.append(("DEBRIEF", debrief.strip()))

    # 3. SITUATION_SUMMARY
    source_key = case["source_key"]
    sit_content = None
    if source_key == "PLAY_STORE":
        sit_dict = case.get("structured_situation", {})
        sit_content = sit_dict.get("retrieval_situation")
    elif source_key == "REDDIT":
        sit_dict = case.get("structured_situation", {})
        sit_content = sit_dict.get("situation_description") or sit_dict.get("research_interpretation")
    elif source_key == "USER_INTERVIEW":
        sit_dict = case.get("structured_situation", {})
        title = sit_dict.get("scenario_title", "")
        desc = sit_dict.get("situation_description", "")
        interp = sit_dict.get("research_interpretation", "")
        parts = [p for p in [title, desc, interp] if p]
        sit_content = " | ".join(parts) if parts else None

    if sit_content and sit_content.strip() and sit_content.strip() != "UNKNOWN / NOT_STATED":
        chunks.append(("SITUATION_SUMMARY", sit_content.strip()))

    # 4. JTBD
    jtbd = case.get("job_to_be_done")
    if jtbd and jtbd.strip() and jtbd.strip() != "UNKNOWN / NOT_STATED":
        chunks.append(("JTBD", jtbd.strip()))

    return chunks


# =============================================================================
# 4. ASYNCPG DATABASE INGESTION ENGINE
# =============================================================================

async def execute_ingestion(
    normalized_cases: List[Dict[str, Any]],
    db_url: str,
    embedder: LocalEmbedder,
    dry_run: bool = False,
    batch_size: int = 50,
) -> Dict[str, Any]:
    """
    Executes the ingestion workflow:
    - Registers sources
    - Upserts evidence_cases
    - Chunks each case & computes 384-dim embeddings
    - Replaces chunks idempotently
    - Runs post-ingestion validation
    """
    if dry_run:
        logger.info("[DRY-RUN MODE] Validating chunking and embedding generation without database writes...")
        all_chunks: List[Tuple[Dict[str, Any], str, str]] = []
        for c in normalized_cases:
            case_chunks = extract_chunks_for_case(c)
            for ctype, content in case_chunks:
                all_chunks.append((c, ctype, content))

        logger.info(f"[DRY-RUN] Generated {len(all_chunks)} chunks across {len(normalized_cases)} cases.")
        sample_texts = [content for _, _, content in all_chunks[:5]]
        sample_vecs = embedder.encode_batch(sample_texts)
        for i, vec in enumerate(sample_vecs):
            if len(vec) != 384:
                raise ValueError(f"Sample vector {i} dimension mismatch: expected 384, got {len(vec)}")
        logger.info(f"[DRY-RUN] Local embedder validated on sample chunks. Dimension = {len(sample_vecs[0])}.")
        return {
            "status": "DRY_RUN_SUCCESS",
            "cases_validated": len(normalized_cases),
            "chunks_projected": len(all_chunks),
            "vector_dimension": 384,
            "database_written": False,
        }

    # Live Database Ingestion
    import asyncpg

    if db_url.startswith("postgres://"):
        db_url = "postgresql://" + db_url[len("postgres://"):]

    logger.info("Connecting to Supabase PostgreSQL...")
    conn = await asyncpg.connect(db_url, statement_cache_size=0)

    try:
        async with conn.transaction():
            # -----------------------------------------------------------------
            # 1. Source Registration (Idempotent)
            # -----------------------------------------------------------------
            logger.info("Step 1: Registering canonical sources...")
            source_definitions = [
                {
                    "source_type": "PLAY_STORE",
                    "name": "Google Play Store Public Reviews",
                    "document_reference": "raw_reviews_dataset.json",
                    "provenance_metadata": json.dumps({"authoritative_dataset": "part1_playstore_evidence_245_authoritative.json"}),
                },
                {
                    "source_type": "REDDIT",
                    "name": "Reddit r/googlephotos Power-User Discussions",
                    "document_reference": "reddit reviews .docx",
                    "provenance_metadata": json.dumps({"authoritative_dataset": "reddit_evidence_dataset.json"}),
                },
                {
                    "source_type": "USER_INTERVIEW",
                    "name": "1:1 Behavioral Retrieval Testing Episodes",
                    "document_reference": "GOOGLE PHOTOS INTERVIEW (1).docx",
                    "provenance_metadata": json.dumps({"authoritative_dataset": "interview_evidence_dataset.json"}),
                },
            ]

            source_id_map: Dict[str, str] = {}
            for s in source_definitions:
                existing_id = await conn.fetchval(
                    "SELECT id FROM sources WHERE source_type = $1;",
                    s["source_type"],
                )
                if existing_id:
                    source_id_map[s["source_type"]] = str(existing_id)
                else:
                    new_id = await conn.fetchval(
                        """
                        INSERT INTO sources (source_type, name, document_reference, provenance_metadata)
                        VALUES ($1, $2, $3, $4::jsonb)
                        RETURNING id;
                        """,
                        s["source_type"],
                        s["name"],
                        s["document_reference"],
                        s["provenance_metadata"],
                    )
                    source_id_map[s["source_type"]] = str(new_id)

            logger.info(f"Sources registered/resolved: {list(source_id_map.keys())}")

            # -----------------------------------------------------------------
            # 2. Upsert evidence_cases
            # -----------------------------------------------------------------
            logger.info("Step 2: Normalizing and upserting 308 evidence_cases...")
            case_id_map: Dict[str, str] = {}

            for case in normalized_cases:
                sid = source_id_map[case["source_key"]]
                row_id = await conn.fetchval(
                    """
                    INSERT INTO evidence_cases (
                        source_id, external_id, raw_text, user_debrief, app_version,
                        rating, methodology, evidence_type, failure_mode, job_to_be_done,
                        signal_strength, category_tags, structured_situation
                    ) VALUES (
                        $1, $2, $3, $4, $5,
                        $6, $7, $8, $9, $10,
                        $11, $12, $13::jsonb
                    )
                    ON CONFLICT (external_id) DO UPDATE SET
                        source_id = EXCLUDED.source_id,
                        raw_text = EXCLUDED.raw_text,
                        user_debrief = EXCLUDED.user_debrief,
                        app_version = EXCLUDED.app_version,
                        rating = EXCLUDED.rating,
                        methodology = EXCLUDED.methodology,
                        evidence_type = EXCLUDED.evidence_type,
                        failure_mode = EXCLUDED.failure_mode,
                        job_to_be_done = EXCLUDED.job_to_be_done,
                        signal_strength = EXCLUDED.signal_strength,
                        category_tags = EXCLUDED.category_tags,
                        structured_situation = EXCLUDED.structured_situation
                    RETURNING id;
                    """,
                    sid,
                    case["external_id"],
                    case["raw_text"],
                    case["user_debrief"],
                    case["app_version"],
                    case["rating"],
                    case["methodology"],
                    case["evidence_type"],
                    case["failure_mode"],
                    case["job_to_be_done"],
                    case["signal_strength"],
                    case["category_tags"],
                    json.dumps(case["structured_situation"]),
                )
                case_id_map[case["external_id"]] = str(row_id)

            logger.info(f"Upserted {len(case_id_map)} evidence_cases successfully.")

            # -----------------------------------------------------------------
            # 3. Deterministic Chunking & Batch Embeddings
            # -----------------------------------------------------------------
            logger.info("Step 3: Generating chunks and 384-dimensional embeddings...")
            all_chunks: List[Tuple[str, str, str]] = []  # (case_uuid, chunk_type, content)

            for case in normalized_cases:
                cid = case_id_map[case["external_id"]]
                c_chunks = extract_chunks_for_case(case)
                for ctype, content in c_chunks:
                    all_chunks.append((cid, ctype, content))

            logger.info(f"Total chunks to insert: {len(all_chunks)} across {len(normalized_cases)} cases.")

            # Compute embeddings in batches
            chunk_contents = [c[2] for c in all_chunks]
            chunk_vectors = embedder.encode_batch(chunk_contents, batch_size=batch_size)

            # Clear existing chunks for upserted cases (idempotent regeneration)
            case_uuids = list(case_id_map.values())
            await conn.execute(
                "DELETE FROM evidence_chunks WHERE evidence_case_id = ANY($1::uuid[]);",
                case_uuids,
            )

            # Insert chunks in batches
            logger.info("Inserting chunk vectors into evidence_chunks...")
            insert_batch_size = 100
            for i in range(0, len(all_chunks), insert_batch_size):
                batch_slice = all_chunks[i : i + insert_batch_size]
                batch_vecs = chunk_vectors[i : i + insert_batch_size]

                for (case_uuid, ctype, content), vec in zip(batch_slice, batch_vecs):
                    vec_str = str(vec)
                    await conn.execute(
                        """
                        INSERT INTO evidence_chunks (
                            evidence_case_id, chunk_type, content, embedding
                        ) VALUES ($1, $2, $3, $4::vector(384));
                        """,
                        case_uuid,
                        ctype,
                        content,
                        vec_str,
                    )

            logger.info(f"Inserted {len(all_chunks)} chunk vectors successfully.")

            # -----------------------------------------------------------------
            # 4. Post-Ingestion Validation Gates
            # -----------------------------------------------------------------
            logger.info("Step 4: Executing post-ingestion validation gates...")
            source_count = await conn.fetchval("SELECT count(*) FROM sources;")
            unsolicited_count = await conn.fetchval(
                "SELECT count(*) FROM evidence_cases WHERE methodology = 'UNSOLICITED_PUBLIC';"
            )
            prompted_count = await conn.fetchval(
                "SELECT count(*) FROM evidence_cases WHERE methodology = 'PROMPTED_INTERVIEW';"
            )
            total_cases = await conn.fetchval("SELECT count(*) FROM evidence_cases;")
            total_chunks = await conn.fetchval("SELECT count(*) FROM evidence_chunks;")
            null_embeddings = await conn.fetchval(
                "SELECT count(*) FROM evidence_chunks WHERE embedding IS NULL;"
            )
            null_mandatory = await conn.fetchval(
                """
                SELECT count(*) FROM evidence_cases
                WHERE external_id IS NULL OR raw_text IS NULL OR methodology IS NULL OR evidence_type IS NULL;
                """
            )

            # Assert all validation gates
            assert source_count == 3, f"Gate failed: Expected 3 sources, got {source_count}"
            assert unsolicited_count == 283, f"Gate failed: Expected 283 unsolicited, got {unsolicited_count}"
            assert prompted_count == 25, f"Gate failed: Expected 25 prompted, got {prompted_count}"
            assert total_cases == 308, f"Gate failed: Expected 308 cases, got {total_cases}"
            assert total_chunks >= 308, f"Gate failed: Expected >= 308 chunks, got {total_chunks}"
            assert null_embeddings == 0, f"Gate failed: Found {null_embeddings} NULL embeddings"
            assert null_mandatory == 0, f"Gate failed: Found {null_mandatory} cases with NULL mandatory fields"

            logger.info("ALL POST-INGESTION VALIDATION GATES: PASS (100% SUCCESS)")

            return {
                "status": "LIVE_INGESTION_SUCCESS",
                "sources_count": source_count,
                "unsolicited_count": unsolicited_count,
                "prompted_count": prompted_count,
                "total_cases": total_cases,
                "total_chunks": total_chunks,
                "null_embeddings": null_embeddings,
                "vector_dimension": 384,
                "database_written": True,
            }

    finally:
        await conn.close()


# =============================================================================
# 5. CLI ENTRYPOINT
# =============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Master research evidence ingestion worker into Supabase (Step 3)."
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default="config/ingestion_manifest.json",
        help="Path to declarative ingestion manifest",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate manifest, sources, mapping, chunking, and embeddings with ZERO database writes",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default=None,
        help="Override database connection string (defaults to DATABASE_URL in backend/.env)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for embedding generation",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override embedding model candidate (defaults to EMBEDDING_MODEL_NAME or intfloat/multilingual-e5-small)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    manifest_path = Path(args.manifest)
    base_dir = manifest_path.parent.parent if manifest_path.is_absolute() else PROJECT_ROOT

    # 4. Resolve local embedder
    embedder = LocalEmbedder.get_instance(model_name=args.model)

    print("================================================================================")
    print("GOOGLE PHOTOS DISCOVERY ENGINE — STEP 3 EVIDENCE INGESTION PIPELINE")
    print(f"Mode: {'DRY RUN (NO DB WRITES)' if args.dry_run else 'LIVE DATABASE INGESTION'}")
    print(f"Model Candidate: {embedder.model_name} (Dim: {embedder.expected_dim})")
    print("================================================================================")

    # 1. Manifest pre-flight validation
    manifest = load_and_validate_manifest(manifest_path)

    # 2. Load authoritative datasets
    ps_records, rd_records, it_records = load_authoritative_datasets(manifest, base_dir)

    # 3. Normalize records and check global uniqueness
    normalized_cases = normalize_all_records(ps_records, rd_records, it_records)

    # 5. Database connection string
    db_url = args.db_url or os.getenv("DATABASE_URL")
    if not args.dry_run and (not db_url or "PLACEHOLDER" in db_url):
        logger.error("DATABASE_URL is not configured in backend/.env or environment. Aborting.")
        sys.exit(1)

    # 6. Execute ingestion (or dry run)
    try:
        results = asyncio.run(
            execute_ingestion(
                normalized_cases=normalized_cases,
                db_url=db_url or "",
                embedder=embedder,
                dry_run=args.dry_run,
                batch_size=args.batch_size,
            )
        )
    except Exception as e:
        logger.error(f"Ingestion failed with exception: {type(e).__name__}: {str(e)}", exc_info=True)
        sys.exit(1)

    print("\n--------------------------------------------------------------------------------")
    print("INGESTION EXECUTION REPORT:")
    for k, v in results.items():
        print(f"  {k}: {v}")
    print("--------------------------------------------------------------------------------\n")


if __name__ == "__main__":
    main()
