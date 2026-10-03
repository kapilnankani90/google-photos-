"""
PostgreSQL Lexical FTS Multi-Path Retriever (Stage 4–6).

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 10–13, 18.2, 24)
- part1_discovery_engine_architecture_final.md (Stages 4–6)
- database/migrations/001_initial_schema.sql (search_vector TSVECTOR, idx_chunks_fts GIN)

Active Runtime Path:
- Path 2: Full-Text Lexical Search on PostgreSQL tsvector GIN index (idx_chunks_fts).
- Path 3: Structured Metadata Filtering (category_tags GIN array, methodology, rating).
- Path 4: Temporal Boundary Filtering (SQL created_at date ranges).
- Path 1: Semantic vector search (pgvector) is strictly bypassed due to Step 5 NO_ELIGIBLE_CANDIDATE.

Zero SentenceTransformer imports, zero heavy model weights in memory.
"""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
import os
import re
import logging
from datetime import datetime
import asyncpg

from app.core.config import settings
from app.representation.models import V2MemoryRepresentation
from app.representation.persistence import _get_clean_db_url
from app.retrieval.models import (
    RetrievalFilter,
    ScoreBreakdown,
    CandidateResult,
    CoverageEvaluation,
    DiscoveryResponse,
)
from app.retrieval.signals import generate_retrieval_signals, RetrievalSignals

logger = logging.getLogger("LexicalRetriever")


class MultiPathRetriever:
    """
    Coordinates multi-path candidate discovery in PostgreSQL Lexical FTS mode.
    Executes GIN-indexed tsvector search, applies structured & temporal filters,
    performs deterministic coverage checking, and computes compositional scores.
    """

    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url

    async def retrieve(
        self,
        representation: V2MemoryRepresentation,
        filters: Optional[RetrievalFilter] = None,
        top_k: int = 10,
        enable_recovery: bool = True,
        conn: Optional[asyncpg.Connection] = None,
        db_url: Optional[str] = None,
    ) -> DiscoveryResponse:
        """
        Executes end-to-end multi-path discovery (Stages 3–6) using PostgreSQL Lexical FTS.
        Guarantees zero LocalEmbedder instantiations and zero vector computations.
        """
        # Stage 3: Retrieval Signal Generation
        signals = generate_retrieval_signals(representation)
        search_terms = signals.search_query_terms

        if not search_terms:
            # Empty query terms fallback: return clean empty discovery response
            return DiscoveryResponse(
                raw_input=representation.raw_input,
                v2_frame=representation.model_dump(),
                retrieval_signals=signals.model_dump(),
                coverage_status="COVERAGE_INSUFFICIENT_EMPTY_QUERY",
                controlled_recovery_triggered=False,
                candidate_pool_size=0,
                results=[],
            )

        # Primary FTS query text (quoted words for clean websearch parsing)
        primary_query_str = " ".join(search_terms)

        async def _execute_search(c: asyncpg.Connection) -> DiscoveryResponse:
            # 1. Primary Lexical FTS pass
            raw_rows, recovery_triggered = await self._query_postgres_fts(
                c=c,
                query_str=primary_query_str,
                signals=signals,
                filters=filters,
                limit=max(top_k * 3, 20),
                broaden=False,
            )

            # 2. Candidate Coverage Check (Stage 4)
            coverage = self._evaluate_coverage(raw_rows, signals)

            # 3. Controlled Recovery (Stage 4): execute single broadening pass if insufficient
            if (
                enable_recovery
                and coverage.status in ("INSUFFICIENT_VOLUME", "INSUFFICIENT_DIMENSIONAL_COVERAGE")
                and len(search_terms) > 1
            ):
                logger.info("Coverage insufficient (%s). Executing Controlled Recovery broadening pass...", coverage.status)
                broadened_rows, _ = await self._query_postgres_fts(
                    c=c,
                    query_str=primary_query_str,
                    signals=signals,
                    filters=filters,
                    limit=max(top_k * 3, 20),
                    broaden=True,
                )
                if len(broadened_rows) > len(raw_rows):
                    raw_rows = broadened_rows
                    recovery_triggered = True
                    coverage = self._evaluate_coverage(raw_rows, signals)
                    coverage.recovery_triggered = True

            # 4. Compositional Matching & Scoring (Stage 5)
            scored_candidates = self._score_candidates(raw_rows, signals)

            # 5. Result Organization & Truncation (Stage 6)
            top_results = scored_candidates[:top_k]
            for idx, cand in enumerate(top_results, start=1):
                cand.rank = idx

            return DiscoveryResponse(
                raw_input=representation.raw_input,
                v2_frame=representation.model_dump(),
                retrieval_signals=signals.model_dump(),
                coverage_status=coverage.status,
                controlled_recovery_triggered=recovery_triggered,
                candidate_pool_size=len(scored_candidates),
                results=top_results,
            )

        if conn is not None:
            return await _execute_search(conn)
        else:
            target_url = _get_clean_db_url(db_url or self.db_url)
            c = await asyncpg.connect(target_url, statement_cache_size=0)
            try:
                return await _execute_search(c)
            finally:
                await c.close()

    async def _query_postgres_fts(
        self,
        c: asyncpg.Connection,
        query_str: str,
        signals: RetrievalSignals,
        filters: Optional[RetrievalFilter],
        limit: int = 50,
        broaden: bool = False,
    ) -> tuple[List[Dict[str, Any]], bool]:
        """
        Builds and executes parameterized SQL query utilizing PostgreSQL GIN index idx_chunks_fts.
        Supports structured filters (category_tags, methodology, rating) and temporal filters.
        """
        conditions = []
        params = []
        param_idx = 1

        # Lexical FTS condition on evidence_chunks.search_vector
        if broaden:
            # Broadened OR-clause query: 'term1 | term2 | ...'
            sanitized_terms = [re.sub(r"[^\w]", "", t) for t in signals.search_query_terms if len(t) > 1]
            if signals.bound_attributes:
                # In controlled recovery, preserve entity constraints and do not broaden to loose attribute modifiers alone
                bound_attr_terms = set()
                for b in signals.bound_attributes:
                    attr_val = b.get("attribute", "")
                    for token in attr_val.lower().split():
                        cleaned = re.sub(r"[^\w]", "", token)
                        if cleaned:
                            bound_attr_terms.add(cleaned)
                broadened_terms = [t for t in sanitized_terms if t.lower() not in bound_attr_terms]
                if not broadened_terms:
                    broadened_terms = sanitized_terms
            else:
                broadened_terms = sanitized_terms

            or_tsquery = " | ".join(broadened_terms) if broadened_terms else query_str
            tsquery_expr = f"to_tsquery('english', ${param_idx})"
            params.append(or_tsquery)
        else:
            # Standard AND-oriented websearch query
            tsquery_expr = f"websearch_to_tsquery('english', ${param_idx})"
            params.append(query_str)

        conditions.append(f"ec.search_vector @@ q.query")
        param_idx += 1

        # Structured Filters on evidence_cases
        if filters:
            if filters.methodology:
                conditions.append(f"c.methodology = ${param_idx}")
                params.append(filters.methodology)
                param_idx += 1

            if filters.evidence_type:
                conditions.append(f"c.evidence_type = ${param_idx}")
                params.append(filters.evidence_type)
                param_idx += 1

            if filters.failure_mode:
                conditions.append(f"c.failure_mode = ${param_idx}")
                params.append(filters.failure_mode)
                param_idx += 1

            if filters.rating is not None:
                conditions.append(f"c.rating = ${param_idx}")
                params.append(filters.rating)
                param_idx += 1

            if filters.signal_strength:
                conditions.append(f"c.signal_strength = ${param_idx}")
                params.append(filters.signal_strength)
                param_idx += 1

            if filters.category_tags:
                conditions.append(f"c.category_tags && ${param_idx}::text[]")
                params.append(filters.category_tags)
                param_idx += 1

            # Temporal Filters
            if filters.start_date:
                conditions.append(f"c.created_at >= ${param_idx}")
                params.append(filters.start_date)
                param_idx += 1

            if filters.end_date:
                conditions.append(f"c.created_at <= ${param_idx}")
                params.append(filters.end_date)
                param_idx += 1

        # Temporal constraint from memory representation signals if not overridden by filter
        if (not filters or not filters.start_date) and signals.temporal_interval:
            interval = signals.temporal_interval
            if interval.get("start_date"):
                try:
                    s_dt = datetime.fromisoformat(interval["start_date"])
                    conditions.append(f"c.created_at >= ${param_idx}")
                    params.append(s_dt)
                    param_idx += 1
                except Exception:
                    pass

            if (not filters or not filters.end_date) and interval.get("end_date"):
                try:
                    e_dt = datetime.fromisoformat(interval["end_date"])
                    conditions.append(f"c.created_at <= ${param_idx}")
                    params.append(e_dt)
                    param_idx += 1
                except Exception:
                    pass

        params.append(limit)
        limit_param_idx = param_idx

        where_clause = " AND ".join(conditions)

        sql = f"""
            SELECT 
                ec.id AS chunk_id,
                ec.evidence_case_id,
                ec.chunk_type,
                ec.content,
                ec.created_at AS chunk_created_at,
                c.external_id,
                c.raw_text,
                c.user_debrief,
                c.rating,
                c.methodology,
                c.evidence_type,
                c.failure_mode,
                c.category_tags,
                c.created_at AS case_created_at,
                ts_rank(ec.search_vector, q.query) AS lexical_rank_score
            FROM evidence_chunks ec
            JOIN evidence_cases c ON ec.evidence_case_id = c.id,
            {tsquery_expr} q(query)
            WHERE {where_clause}
            ORDER BY lexical_rank_score DESC, ec.created_at DESC
            LIMIT ${limit_param_idx};
        """

        try:
            records = await c.fetch(sql, *params)
            return [dict(r) for r in records], broaden
        except Exception as err:
            logger.error("Error executing PostgreSQL Lexical FTS: %s", err)
            # Safe degradation: return empty list on malformed tsquery
            return [], broaden

    def _evaluate_coverage(self, rows: List[Dict[str, Any]], signals: RetrievalSignals) -> CoverageEvaluation:
        """Evaluates volume, spatial representation, and temporal span heuristics (Section 11)."""
        count = len(rows)
        if count == 0:
            return CoverageEvaluation(
                status="INSUFFICIENT_VOLUME",
                candidate_count=0,
                details={"reason": "Zero candidate chunks recovered by lexical FTS query."},
            )

        if count < 5 and len(signals.search_query_terms) >= 2:
            return CoverageEvaluation(
                status="INSUFFICIENT_VOLUME",
                candidate_count=count,
                details={"reason": f"Pool volume ({count}) below multi-clue threshold (5)."},
            )

        # Spatial check: if query has spatial cues, verify representation
        if signals.spatial_cues:
            spatial_found = False
            for r in rows:
                content_lower = (r.get("content") or "").lower()
                raw_lower = (r.get("raw_text") or "").lower()
                if any(cue.lower() in content_lower or cue.lower() in raw_lower for cue in signals.spatial_cues):
                    spatial_found = True
                    break
            if not spatial_found:
                return CoverageEvaluation(
                    status="INSUFFICIENT_DIMENSIONAL_COVERAGE",
                    candidate_count=count,
                    details={"reason": "Query expressed spatial cue but zero retrieved candidates match spatial dimension."},
                )

        return CoverageEvaluation(
            status="COVERAGE_SUFFICIENT",
            candidate_count=count,
            details={"volume": count},
        )

    def _score_candidates(self, rows: List[Dict[str, Any]], signals: RetrievalSignals) -> List[CandidateResult]:
        """
        Executes Compositional Matching (Stage 5):
        FinalScore = BaseRRF + BoundBonus - DistractorPenalty.
        """
        candidates: List[CandidateResult] = []

        for idx, row in enumerate(rows, start=1):
            # Base RRF from lexical rank position (Section 10.1)
            base_rrf = 1.0 / (60.0 + idx)

            content = row.get("content", "")
            raw_text = row.get("raw_text", "")
            searchable_text = f"{content} {raw_text}".lower()

            # Bound entity-attribute bonus (+1.5 per matched binding)
            bound_bonus = 0.0
            for binding in signals.bound_attributes:
                ent = binding.get("entity", "").lower()
                attr = binding.get("attribute", "").lower()
                if ent and attr:
                    if ent in searchable_text and attr in searchable_text:
                        bound_bonus += 1.5

            # Distractor penalty: penalize candidates matching only the attribute of a bound pair
            # while missing the required entity (Section 13.1)
            distractor_penalty = 0.0
            for binding in signals.bound_attributes:
                ent = binding.get("entity", "").lower()
                attr = binding.get("attribute", "").lower()
                if ent and attr:
                    if attr in searchable_text and ent not in searchable_text:
                        distractor_penalty += 1.0

            final_score = base_rrf + bound_bonus - distractor_penalty

            score_breakdown = ScoreBreakdown(
                base_rrf=round(base_rrf, 4),
                bound_bonus=round(bound_bonus, 2),
                distractor_penalty=round(distractor_penalty, 2),
            )

            metadata = {
                "external_id": row.get("external_id"),
                "methodology": row.get("methodology"),
                "rating": row.get("rating"),
                "failure_mode": row.get("failure_mode"),
                "category_tags": row.get("category_tags") or [],
                "evidence_type": row.get("evidence_type"),
                "case_created_at": row.get("case_created_at").isoformat() if row.get("case_created_at") else None,
            }

            candidate_id = str(row.get("chunk_id") or row.get("external_id") or f"cand_{idx}")

            cand = CandidateResult(
                candidate_id=candidate_id,
                chunk_id=str(row["chunk_id"]) if row.get("chunk_id") else None,
                case_id=str(row["evidence_case_id"]) if row.get("evidence_case_id") else row.get("external_id"),
                chunk_type=row.get("chunk_type"),
                content=content,
                rank=idx,
                score=round(final_score, 4),
                score_breakdown=score_breakdown,
                retrieval_paths=["lexical_fts"],
                metadata=metadata,
            )
            candidates.append(cand)

        # Deterministic sorting (Stage 6): score DESC, then candidate_id ASC for tie-breaking
        candidates.sort(key=lambda c: (-c.score, c.candidate_id))
        return candidates
