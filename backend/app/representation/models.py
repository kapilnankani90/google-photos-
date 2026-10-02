"""
V2 Memory Representation Models.

Governed strictly by:
- part1_memory_representation_schema_v2.md
- part1_discovery_engine_implementation_spec.md (Section 7.1)
- database/migrations/001_initial_schema.sql (Table: memory_representations)

Enforces locked V2 schema contract with extra="forbid", zero ungrounded field fabrication,
and preservation of verbatim raw_input query provenance.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class PersonConcept(BaseModel):
    """Human individuals or groups identified by kinship, familial role, social position, or demographic count."""
    model_config = ConfigDict(extra="forbid")

    role: str = Field(
        ...,
        description="Kinship or social role (e.g., sister, cousin, brother, maid, watchman, colleague, friends)."
    )
    count: Optional[int] = Field(
        None,
        description="Explicit group count if recalled (e.g., 5 in '5 sisters', 2 in 'two ladies')."
    )
    attributes: List[str] = Field(
        default_factory=list,
        description="Descriptive visual or clothing modifiers bound to this person/group (e.g., ['yellow suit'], ['blue outfit'])."
    )
    possessive: Optional[str] = Field(
        None,
        description="Possessive marker if expressed (e.g., 'my', 'our', 'meri')."
    )


class EventConcept(BaseModel):
    """Milestone event, cultural celebration, or social occasion."""
    model_config = ConfigDict(extra="forbid")

    event_name: str = Field(
        ...,
        description="Primary event name (e.g., wedding, diwali, farewell, birthday, holi, engagement)."
    )
    sub_event: Optional[str] = Field(
        None,
        description="Optional specific ritual or sub-phase (e.g., haldi, rehearsal, farewell lunch)."
    )


class ObjectConcept(BaseModel):
    """Salient physical props, vehicles, food preparations, or utility documents."""
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ...,
        description="Name of physical object or document (e.g., cake, bike, papaya, ring box, diya, truck, boarding pass, ice)."
    )
    attributes: List[str] = Field(
        default_factory=list,
        description="Descriptive visual modifiers bound directly to this object (e.g., ['white'] for bike, ['yellow'] for truck)."
    )
    possessive: Optional[str] = Field(
        None,
        description="Possessive marker if expressed (e.g., 'my', 'our')."
    )


class TemporalConcept(BaseModel):
    """Coarse calendar, relative elapsed, or specific temporal anchor."""
    model_config = ConfigDict(extra="forbid")

    raw_time_expression: str = Field(
        ...,
        description="Verbatim temporal phrase (e.g., 'around 4 years ago', '2021', 'July 2016', 'Holi 2020')."
    )
    coarse_value: Optional[str] = Field(
        None,
        description="Extracted year or coarse era if identifiable (e.g., '2021', '2016', '4 years ago')."
    )
    temporal_nature: Optional[
        Literal["COARSE_YEAR_ERA", "RELATIVE_OFFSET", "SEASON_EVENT_BOUND", "EXACT_MONTH_YEAR"]
    ] = Field(
        None,
        description="Broad characterization of the temporal anchor without imposing rigid timestamps."
    )


class V2MemoryRepresentation(BaseModel):
    """
    Evidence-grounded V2 Memory Representation Schema.
    Bridges raw natural-language user memory descriptions into structured retrieval frames.
    """
    model_config = ConfigDict(extra="forbid")

    raw_input: str = Field(
        ...,
        description="Verbatim user query or natural-language memory description exactly as provided."
    )
    people: List[PersonConcept] = Field(
        default_factory=list,
        description="People recalled by social, familial, or occupational role."
    )
    events: Optional[EventConcept] = Field(
        None,
        description="Milestone event, cultural celebration, or social occasion."
    )
    objects: List[ObjectConcept] = Field(
        default_factory=list,
        description="Salient physical props, vehicles, food preparations, or utility documents."
    )
    actions: List[str] = Field(
        default_factory=list,
        description="Dynamic activities, physical sports, interactions, or bodily poses."
    )
    temporal: Optional[TemporalConcept] = Field(
        None,
        description="Coarse calendar, relative elapsed, or specific temporal anchor."
    )
    literal_text: List[str] = Field(
        default_factory=list,
        description="Literal alphanumeric text remembered as physically printed on an object, document, or screen."
    )
    spatial_setting: Optional[str] = Field(
        None,
        description="Broad geographic destination, landscape type, or architectural boundary (e.g., 'mountain', 'beach', 'gate', 'rohtang', 'Mussoorie')."
    )

    def to_db_dict(self) -> Dict[str, Any]:
        """
        Converts the representation into dictionary format matching the PostgreSQL columns
        of the memory_representations table.
        """
        return {
            "raw_input": self.raw_input,
            "people": [p.model_dump() for p in self.people],
            "events": self.events.model_dump() if self.events else None,
            "objects": [o.model_dump() for o in self.objects],
            "actions": self.actions,
            "temporal": self.temporal.model_dump() if self.temporal else None,
            "literal_text": self.literal_text,
            "spatial_setting": self.spatial_setting,
        }
