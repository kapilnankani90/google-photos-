"""
Retrieval & Scoring Data Models.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 8, 10–13, 18.2)
- part1_discovery_engine_architecture_final.md (Stages 3–6)

Provides Pydantic data models for structured filters, candidate results,
coverage evaluations, and discovery engine responses in Lexical FTS mode.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class RetrievalFilter(BaseModel):
    """Structured and temporal filtering criteria for Candidate Discovery (Stage 4)."""
    model_config = ConfigDict(extra="forbid")

    source_type: Optional[str] = Field(None, description="Filter by source type (PLAY_STORE, REDDIT, USER_INTERVIEW)")
    methodology: Optional[str] = Field(None, description="Filter by methodology (UNSOLICITED_PUBLIC, PROMPTED_INTERVIEW)")
    evidence_type: Optional[str] = Field(None, description="Filter by evidence type (FAILURE, SUCCESS, NEUTRAL)")
    failure_mode: Optional[str] = Field(None, description="Filter by documented failure mode")
    rating: Optional[int] = Field(None, description="Filter by 1-5 star rating")
    category_tags: Optional[List[str]] = Field(None, description="Filter by category tags (uses GIN array overlap)")
    signal_strength: Optional[str] = Field(None, description="Filter by signal strength (LOW, MEDIUM, HIGH)")
    start_date: Optional[datetime] = Field(None, description="Earliest creation timestamp")
    end_date: Optional[datetime] = Field(None, description="Latest creation timestamp")


class ScoreBreakdown(BaseModel):
    """Detailed score components for auditable compositional ranking."""
    model_config = ConfigDict(extra="forbid")

    base_rrf: float = Field(..., description="Reciprocal Rank Fusion base score from lexical FTS")
    bound_bonus: float = Field(0.0, description="Compositional bonus for bound entity-attribute co-occurrence (+1.5)")
    distractor_penalty: float = Field(0.0, description="Penalty for conflicting dominant attributes")


class CandidateResult(BaseModel):
    """Ranked candidate retrieved via multi-path discovery."""
    model_config = ConfigDict(extra="forbid")

    candidate_id: str = Field(..., description="Unique identifier of candidate (chunk UUID or external_id)")
    chunk_id: Optional[str] = Field(None, description="Evidence chunk UUID")
    case_id: Optional[str] = Field(None, description="Parent evidence case UUID or external_id")
    chunk_type: Optional[str] = Field(None, description="Type of chunk (RAW_QUOTE, DEBRIEF, SITUATION_SUMMARY, JTBD)")
    content: str = Field(..., description="Text content of the retrieved chunk/caption")
    rank: int = Field(..., description="1-indexed final rank position")
    score: float = Field(..., description="Final composite score")
    score_breakdown: ScoreBreakdown = Field(..., description="Auditable breakdown of scoring components")
    retrieval_paths: List[str] = Field(default_factory=lambda: ["lexical_fts"], description="Active retrieval paths")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Associated case metadata")


class CoverageEvaluation(BaseModel):
    """Results of Candidate Coverage Checking (Stage 4)."""
    model_config = ConfigDict(extra="forbid")

    status: str = Field(..., description="Coverage status: COVERAGE_SUFFICIENT, INSUFFICIENT_VOLUME, etc.")
    candidate_count: int = Field(..., description="Number of candidates in initial pool")
    recovery_triggered: bool = Field(False, description="Whether Controlled Recovery broadening was executed")
    details: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic coverage metrics")


class DiscoveryResponse(BaseModel):
    """Standard response schema for Discovery Engine retrieval (Section 18.2)."""
    model_config = ConfigDict(extra="forbid")

    raw_input: str = Field(..., description="Original user natural language query")
    v2_frame: Dict[str, Any] = Field(..., description="Parsed V2 memory representation")
    retrieval_signals: Dict[str, Any] = Field(..., description="Derived retrieval signals")
    coverage_status: str = Field(..., description="Stage 4 coverage outcome")
    controlled_recovery_triggered: bool = Field(False, description="Whether broadening recovery was triggered")
    candidate_pool_size: int = Field(..., description="Total candidates recovered")
    results: List[CandidateResult] = Field(default_factory=list, description="Ranked list of top candidate results")
