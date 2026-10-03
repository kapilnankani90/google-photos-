"""
Retrieval Signal Generation Module (Stage 3).

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Section 8)
- part1_discovery_engine_operating_spec_final.md

Translates an interpreted V2MemoryRepresentation into actionable search probes
and query terms for PostgreSQL Lexical FTS, isolating code-mixed Hinglish particles
while preserving compositional entity-attribute bindings.
"""

from typing import List, Optional, Dict, Any
import re
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict

from app.representation.models import V2MemoryRepresentation
from app.representation.rules import strip_vernacular_particles


class RetrievalSignals(BaseModel):
    """Actionable database search probes derived from V2MemoryRepresentation."""
    model_config = ConfigDict(extra="forbid")

    visual_entities: List[str] = Field(default_factory=list, description="Direct entity nouns for visual/object lookup")
    bound_attributes: List[Dict[str, Any]] = Field(default_factory=list, description="Entity-modifier pairs for compositional ranking")
    action_signals: List[str] = Field(default_factory=list, description="High-specificity physical verbs")
    temporal_interval: Optional[Dict[str, Any]] = Field(None, description="Start/End timestamps derived from coarse expressions")
    literal_text_tokens: List[str] = Field(default_factory=list, description="Verbatim tokens for OCR matching")
    spatial_cues: List[str] = Field(default_factory=list, description="Landscape and environment terms")
    search_query_terms: List[str] = Field(default_factory=list, description="Cleaned lexical tokens for PostgreSQL FTS tsquery")


def _derive_temporal_bounds(raw_time: Optional[str], coarse_val: Optional[str]) -> Optional[Dict[str, Any]]:
    """Derives ISO timestamp boundaries from coarse year or relative expressions."""
    val = (coarse_val or raw_time or "").strip().lower()
    if not val:
        return None

    # Year pattern e.g., '2021', '2016'
    year_match = re.search(r"\b(19\d\d|20\d\d)\b", val)
    if year_match:
        year = int(year_match.group(1))
        start_dt = datetime(year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_dt = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        return {
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "coarse_year": year,
            "raw_expression": val,
        }

    # Relative offset e.g., '4 years ago' (assumes reference 2025/2026)
    offset_match = re.search(r"(\d+)\s+years?\s+ago", val)
    if offset_match:
        num_years = int(offset_match.group(1))
        target_year = 2025 - num_years
        start_dt = datetime(target_year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_dt = datetime(target_year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        return {
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "coarse_year": target_year,
            "raw_expression": val,
        }

    return {"raw_expression": val}


def generate_retrieval_signals(representation: V2MemoryRepresentation) -> RetrievalSignals:
    """
    Derives deterministic RetrievalSignals from a V2MemoryRepresentation.
    Applies vernacular particle stripping, entity-attribute binding, and temporal bounding.
    """
    visual_entities: List[str] = []
    bound_attributes: List[Dict[str, Any]] = []
    spatial_cues: List[str] = []
    action_signals: List[str] = []
    literal_text_tokens: List[str] = []
    fts_tokens: List[str] = []

    # 1. Objects & Bound Attributes
    for obj in representation.objects:
        clean_name = strip_vernacular_particles(obj.name).strip()
        if clean_name and clean_name not in visual_entities:
            visual_entities.append(clean_name)
            fts_tokens.append(clean_name)
        for attr in obj.attributes:
            clean_attr = strip_vernacular_particles(attr).strip()
            if clean_attr:
                bound_attributes.append({
                    "entity": clean_name or obj.name,
                    "attribute": clean_attr,
                })
                fts_tokens.append(clean_attr)

    # 2. People & Bound Attributes
    for p in representation.people:
        clean_role = strip_vernacular_particles(p.role).strip()
        if clean_role and clean_role not in visual_entities:
            visual_entities.append(clean_role)
            fts_tokens.append(clean_role)
        for attr in p.attributes:
            clean_attr = strip_vernacular_particles(attr).strip()
            if clean_attr:
                bound_attributes.append({
                    "entity": clean_role or p.role,
                    "attribute": clean_attr,
                })
                fts_tokens.append(clean_attr)

    # 3. Events
    if representation.events:
        clean_event = strip_vernacular_particles(representation.events.event_name).strip()
        if clean_event and clean_event not in visual_entities:
            visual_entities.append(clean_event)
            fts_tokens.append(clean_event)
        if representation.events.sub_event:
            clean_sub = strip_vernacular_particles(representation.events.sub_event).strip()
            if clean_sub and clean_sub not in visual_entities:
                visual_entities.append(clean_sub)
                fts_tokens.append(clean_sub)

    # 4. Spatial Setting
    if representation.spatial_setting:
        clean_spatial = strip_vernacular_particles(representation.spatial_setting).strip()
        if clean_spatial:
            spatial_cues.append(clean_spatial)
            fts_tokens.append(clean_spatial)

    # 5. Actions
    for act in representation.actions:
        clean_act = strip_vernacular_particles(act).strip()
        if clean_act:
            action_signals.append(clean_act)
            fts_tokens.append(clean_act)

    # 6. Literal Text
    for lit in representation.literal_text:
        clean_lit = lit.strip()
        if clean_lit:
            literal_text_tokens.append(clean_lit)
            fts_tokens.append(clean_lit)

    # 7. Fallback: if no structured tokens were found, strip particles from raw_input
    if not fts_tokens:
        cleaned_raw = strip_vernacular_particles(representation.raw_input).strip()
        words = [w.strip() for w in cleaned_raw.split() if len(w.strip()) > 1]
        fts_tokens.extend(words)

    # Deduplicate while preserving order
    seen = set()
    unique_fts_terms = []
    for term in fts_tokens:
        normalized = term.lower()
        if normalized not in seen and len(normalized) > 1:
            seen.add(normalized)
            unique_fts_terms.append(term)

    # 8. Temporal Bounds
    temporal_bounds = None
    if representation.temporal:
        temporal_bounds = _derive_temporal_bounds(
            representation.temporal.raw_time_expression,
            representation.temporal.coarse_value,
        )

    return RetrievalSignals(
        visual_entities=visual_entities,
        bound_attributes=bound_attributes,
        action_signals=action_signals,
        temporal_interval=temporal_bounds,
        literal_text_tokens=literal_text_tokens,
        spatial_cues=spatial_cues,
        search_query_terms=unique_fts_terms,
    )
