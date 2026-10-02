"""
V2 Memory Representation Persistence Layer.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 4.1, 7.1)
- database/migrations/001_initial_schema.sql (Table: memory_representations)

Implements:
1. Idempotent persistence of V2MemoryRepresentation instances to Supabase PostgreSQL.
2. Exact JSONB mapping for people, events, objects, actions, temporal, and literal_text.
3. String mapping for spatial_setting.
4. Strict referential integrity: evidence_case_id foreign key preservation.
5. Strict database safety: NEVER modifies evidence_cases, evidence_chunks, or sources.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, Union
from uuid import UUID

import asyncpg
from app.core.config import settings
from app.representation.models import V2MemoryRepresentation

logger = logging.getLogger("RepresentationPersistence")


def _get_clean_db_url(url: Optional[str] = None) -> str:
    """Normalizes database connection string for asyncpg."""
    raw = url or settings.DATABASE_URL or os.getenv("DATABASE_URL")
    if not raw:
        raise ValueError("DATABASE_URL is not configured.")
    if raw.startswith("postgres://"):
        return "postgresql://" + raw[len("postgres://"):]
    return raw


async def persist_representation(
    representation: V2MemoryRepresentation,
    conn: Optional[asyncpg.Connection] = None,
    db_url: Optional[str] = None,
    evidence_case_id: Optional[Union[str, UUID]] = None,
    is_benchmark_case: bool = False,
) -> str:
    """
    Persists a V2MemoryRepresentation idempotently into the memory_representations table.

    If a record with matching (raw_input, evidence_case_id) already exists,
    it updates the existing row and returns its UUID.
    Otherwise, inserts a new row and returns its UUID.

    Guarantees:
    - Never modifies evidence_cases, evidence_chunks, or sources.
    - Preserves exact verbatim raw_input.
    """
    case_uuid = str(evidence_case_id) if evidence_case_id else None

    # Serialize JSONB components matching PostgreSQL 15 schema
    people_json = json.dumps([p.model_dump() for p in representation.people])
    events_json = json.dumps(representation.events.model_dump()) if representation.events else None
    objects_json = json.dumps([o.model_dump() for o in representation.objects])
    actions_json = json.dumps(representation.actions)
    temporal_json = json.dumps(representation.temporal.model_dump()) if representation.temporal else None
    literal_text_json = json.dumps(representation.literal_text)
    spatial_setting = representation.spatial_setting

    async def _execute(c: asyncpg.Connection) -> str:
        # Check for existing record
        check_query = """
            SELECT id FROM memory_representations
            WHERE raw_input = $1
              AND (
                  (evidence_case_id = $2::uuid) OR
                  (evidence_case_id IS NULL AND $2::uuid IS NULL)
              );
        """
        existing_id = await c.fetchval(check_query, representation.raw_input, case_uuid)

        if existing_id:
            update_query = """
                UPDATE memory_representations
                SET people = $2::jsonb,
                    events = $3::jsonb,
                    objects = $4::jsonb,
                    actions = $5::jsonb,
                    temporal = $6::jsonb,
                    literal_text = $7::jsonb,
                    spatial_setting = $8,
                    is_benchmark_case = $9
                WHERE id = $1
                RETURNING id;
            """
            updated_id = await c.fetchval(
                update_query,
                existing_id,
                people_json,
                events_json,
                objects_json,
                actions_json,
                temporal_json,
                literal_text_json,
                spatial_setting,
                is_benchmark_case,
            )
            logger.info("Updated existing memory_representation id=%s (idempotent)", updated_id)
            return str(updated_id)

        # Insert new record
        insert_query = """
            INSERT INTO memory_representations (
                evidence_case_id,
                raw_input,
                people,
                events,
                objects,
                actions,
                temporal,
                literal_text,
                spatial_setting,
                is_benchmark_case
            )
            VALUES (
                $1::uuid,
                $2,
                $3::jsonb,
                $4::jsonb,
                $5::jsonb,
                $6::jsonb,
                $7::jsonb,
                $8::jsonb,
                $9,
                $10
            )
            RETURNING id;
        """
        new_id = await c.fetchval(
            insert_query,
            case_uuid,
            representation.raw_input,
            people_json,
            events_json,
            objects_json,
            actions_json,
            temporal_json,
            literal_text_json,
            spatial_setting,
            is_benchmark_case,
        )
        logger.info("Inserted new memory_representation id=%s", new_id)
        return str(new_id)

    if conn is not None:
        return await _execute(conn)
    else:
        url = _get_clean_db_url(db_url)
        c = await asyncpg.connect(url, statement_cache_size=0)
        try:
            return await _execute(c)
        finally:
            await c.close()


async def fetch_representation_by_id(
    rep_id: Union[str, UUID],
    conn: Optional[asyncpg.Connection] = None,
    db_url: Optional[str] = None,
) -> Optional[V2MemoryRepresentation]:
    """Retrieves and parses a stored V2MemoryRepresentation by primary key."""
    async def _execute(c: asyncpg.Connection) -> Optional[V2MemoryRepresentation]:
        row = await c.fetchrow(
            """
            SELECT raw_input, people, events, objects, actions, temporal, literal_text, spatial_setting
            FROM memory_representations
            WHERE id = $1::uuid;
            """,
            str(rep_id),
        )
        if not row:
            return None

        # Build payload for Pydantic validation
        raw_input = row["raw_input"]
        people = json.loads(row["people"]) if isinstance(row["people"], str) else (row["people"] or [])
        events = json.loads(row["events"]) if isinstance(row["events"], str) else row["events"]
        objects = json.loads(row["objects"]) if isinstance(row["objects"], str) else (row["objects"] or [])
        actions = json.loads(row["actions"]) if isinstance(row["actions"], str) else (row["actions"] or [])
        temporal = json.loads(row["temporal"]) if isinstance(row["temporal"], str) else row["temporal"]
        literal_text = json.loads(row["literal_text"]) if isinstance(row["literal_text"], str) else (row["literal_text"] or [])
        spatial_setting = row["spatial_setting"]

        data = {
            "raw_input": raw_input,
            "people": people,
            "events": events,
            "objects": objects,
            "actions": actions,
            "temporal": temporal,
            "literal_text": literal_text,
            "spatial_setting": spatial_setting,
        }
        return V2MemoryRepresentation.model_validate(data)

    if conn is not None:
        return await _execute(conn)
    else:
        url = _get_clean_db_url(db_url)
        c = await asyncpg.connect(url, statement_cache_size=0)
        try:
            return await _execute(c)
        finally:
            await c.close()
