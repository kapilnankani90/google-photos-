"""
Structured NLU Schemas for Personal Memory Search.

Governed strictly by Memory Search MVP Requirements:
Captures 10 fundamental memory dimensions:
1. people
2. place/location
3. time/date or approximate time
4. event/activity
5. objects
6. visual attributes
7. scene/environment
8. relationship/context
9. uncertainty/ambiguity
10. original_memory_text

Distinguishes between:
- explicitly stated clues ('explicit')
- inferred/weak clues ('inferred')
- unknown information ('unknown')
"""

from typing import List, Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field, ConfigDict

from app.representation.models import V2MemoryRepresentation, PersonConcept, EventConcept, ObjectConcept, TemporalConcept
from app.retrieval.models import CandidateResult, DiscoveryResponse
from app.retrieval.signals import RetrievalSignals

ClueCertainty = Literal["explicit", "inferred", "unknown"]


class PersonClue(BaseModel):
    """Person or group memory clue."""
    model_config = ConfigDict(extra="ignore")

    role: str = Field(..., description="Role or relationship (e.g. friends, sister, mom, colleagues)")
    count: Optional[int] = Field(None, description="Explicit or inferred group count")
    attributes: List[str] = Field(default_factory=list, description="Descriptive or clothing modifiers")
    possessive: Optional[str] = Field(None, description="Possessive marker (e.g. my, our)")
    certainty: ClueCertainty = Field("explicit", description="Certainty level: explicit vs inferred vs unknown")


class LocationClue(BaseModel):
    """Place or geographic location clue."""
    model_config = ConfigDict(extra="ignore")

    place: str = Field(..., description="Geographic name or landmark (e.g. Goa, Rohtang, Paris, beach)")
    attributes: List[str] = Field(default_factory=list, description="Descriptive modifiers (e.g. near sea, North Goa)")
    certainty: ClueCertainty = Field("explicit", description="Certainty level: explicit vs inferred vs unknown")


class TemporalClue(BaseModel):
    """Time, date, season, or approximate elapsed era clue."""
    model_config = ConfigDict(extra="ignore")

    raw_expression: str = Field(..., description="Verbatim or approximate temporal phrase (e.g. sunset, 4 years ago, 2021)")
    coarse_value: Optional[str] = Field(None, description="Extracted year or time of day anchor (e.g. sunset, 2021)")
    temporal_nature: Optional[str] = Field(None, description="Nature: COARSE_YEAR_ERA, RELATIVE_OFFSET, SEASON_EVENT_BOUND, EXACT_MONTH_YEAR, TIME_OF_DAY")
    certainty: ClueCertainty = Field("explicit", description="Certainty level: explicit vs inferred vs unknown")


class EventActivityClue(BaseModel):
    """Event occasion or dynamic physical activity clue."""
    model_config = ConfigDict(extra="ignore")

    event_name: Optional[str] = Field(None, description="Occasion or trip name (e.g. trip, wedding, vacation)")
    activity: Optional[str] = Field(None, description="Dynamic activity (e.g. standing, skiing, swimming, dinner)")
    certainty: ClueCertainty = Field("explicit", description="Certainty level: explicit vs inferred vs unknown")


class ObjectClue(BaseModel):
    """Salient physical prop, vehicle, animal, or utility document clue."""
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., description="Name of object or prop (e.g. sea, bike, ice, cake)")
    attributes: List[str] = Field(default_factory=list, description="Visual modifiers (e.g. white, vintage)")
    certainty: ClueCertainty = Field("explicit", description="Certainty level: explicit vs inferred vs unknown")


class VisualAttributeClue(BaseModel):
    """Visual aesthetic, color, or lighting clue."""
    model_config = ConfigDict(extra="ignore")

    attribute: str = Field(..., description="Visual detail (e.g. sunset glow, yellow outfit, snow)")
    target_entity: Optional[str] = Field(None, description="Entity this visual applies to (e.g. sky, clothes)")
    certainty: ClueCertainty = Field("explicit", description="Certainty level: explicit vs inferred vs unknown")


class SceneEnvironmentClue(BaseModel):
    """Environmental, weather, or ambient context clue."""
    model_config = ConfigDict(extra="ignore")

    environment: str = Field(..., description="Ambient scene (e.g. seaside, outdoors, mountain, cold)")
    certainty: ClueCertainty = Field("explicit", description="Certainty level: explicit vs inferred vs unknown")


class RelationshipContextClue(BaseModel):
    """Social dynamic or contextual setting clue."""
    model_config = ConfigDict(extra="ignore")

    context: str = Field(..., description="Social context (e.g. with friends, family vacation, solo)")
    certainty: ClueCertainty = Field("explicit", description="Certainty level: explicit vs inferred vs unknown")


class AmbiguityAssessment(BaseModel):
    """Evaluation of ambiguity, hedging, and conversational clarification."""
    model_config = ConfigDict(extra="ignore")

    is_ambiguous: bool = Field(False, description="Whether memory contains significant ambiguity or weak hedges")
    confidence_score: float = Field(1.0, ge=0.0, le=1.0, description="Overall extraction confidence score")
    hedges_detected: List[str] = Field(default_factory=list, description="Hedge words found (e.g. 'maybe', 'think', 'around')")
    ambiguity_reasons: List[str] = Field(default_factory=list, description="Explanation of ambiguity")
    clarification_question: Optional[str] = Field(None, description="Lightweight conversational clarification question if ambiguous")


class MemoryStructuredClues(BaseModel):
    """
    Comprehensive NLU output structuring the 10 memory dimensions,
    explicit vs inferred separation, and ambiguity assessment.
    """
    model_config = ConfigDict(extra="ignore")

    original_memory_text: str = Field(..., description="Verbatim original input text")
    people: List[PersonClue] = Field(default_factory=list)
    place_location: Optional[LocationClue] = None
    time_temporal: Optional[TemporalClue] = None
    event_activity: Optional[EventActivityClue] = None
    objects: List[ObjectClue] = Field(default_factory=list)
    visual_attributes: List[VisualAttributeClue] = Field(default_factory=list)
    scene_environment: Optional[SceneEnvironmentClue] = None
    relationship_context: Optional[RelationshipContextClue] = None
    uncertainty_ambiguity: AmbiguityAssessment = Field(default_factory=AmbiguityAssessment)

    # Summarized views for transparent UI presentation
    explicit_clues: List[str] = Field(default_factory=list, description="List of clues directly stated by user")
    inferred_clues: List[str] = Field(default_factory=list, description="List of clues weakly inferred or qualified with uncertainty")
    unknown_dimensions: List[str] = Field(default_factory=list, description="Dimensions not mentioned by user")


class MemorySearchRequest(BaseModel):
    """Request payload for Memory Search MVP."""
    model_config = ConfigDict(extra="ignore")

    raw_input: str = Field(..., min_length=1, description="Fuzzy natural language memory query")
    top_k: int = Field(8, ge=1, le=100, description="Maximum candidates to retrieve")
    enable_recovery: bool = Field(True, description="Enable controlled recovery broadening if initial pass is sparse")


class MemoryInterpretationResponse(BaseModel):
    """Interpretation-only response for transparent inspection or clarification."""
    model_config = ConfigDict(extra="ignore")

    original_memory_text: str
    llm_provider: Literal["groq", "fallback"]
    model_name: Optional[str] = None
    structured_clues: MemoryStructuredClues
    v2_representation: V2MemoryRepresentation
    is_ambiguous: bool
    clarification_question: Optional[str] = None


class MemorySearchResponse(BaseModel):
    """
    End-to-End Memory Search Response.
    Combines rich Groq NLU interpretation with Discovery Engine retrieval results.
    """
    model_config = ConfigDict(extra="ignore")

    original_memory_text: str
    raw_input: Optional[str] = None
    llm_provider: Literal["groq", "fallback"]
    model_name: Optional[str] = None
    structured_clues: MemoryStructuredClues
    clarification_question: Optional[str] = None
    is_ambiguous: bool

    # Discovery Engine outputs (conforms strictly to DiscoveryResponse contract)
    v2_frame: Union[V2MemoryRepresentation, Dict[str, Any]]
    retrieval_signals: Union[RetrievalSignals, Dict[str, Any]]
    results: List[CandidateResult]
    coverage_status: str
    controlled_recovery_triggered: bool
    candidate_pool_size: int
    execution_time_ms: Optional[float] = None
