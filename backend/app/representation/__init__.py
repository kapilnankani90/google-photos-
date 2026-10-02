"""
Representation Pipeline Module (Step 4).

Governed strictly by:
- part1_memory_representation_schema_v2.md
- part1_discovery_engine_implementation_spec.md (Section 7)

Exposes:
- Pydantic v2 Models: V2MemoryRepresentation, PersonConcept, EventConcept, ObjectConcept, TemporalConcept
- Deterministic rules: parse_deterministically, strip_vernacular_particles, is_ambiguous_query
- Gemini structured fallback: GeminiParserClient
- Memory Interpreter orchestrator: MemoryInterpreter
- Database persistence: persist_representation, fetch_representation_by_id
"""

from app.representation.models import (
    PersonConcept,
    EventConcept,
    ObjectConcept,
    TemporalConcept,
    V2MemoryRepresentation,
)
from app.representation.rules import (
    parse_deterministically,
    strip_vernacular_particles,
    is_ambiguous_query,
    sanitize_input,
)
from app.representation.gemini_parser import GeminiParserClient
from app.representation.interpreter import MemoryInterpreter
from app.representation.persistence import (
    persist_representation,
    fetch_representation_by_id,
)

__all__ = [
    "PersonConcept",
    "EventConcept",
    "ObjectConcept",
    "TemporalConcept",
    "V2MemoryRepresentation",
    "parse_deterministically",
    "strip_vernacular_particles",
    "is_ambiguous_query",
    "sanitize_input",
    "GeminiParserClient",
    "MemoryInterpreter",
    "persist_representation",
    "fetch_representation_by_id",
]
