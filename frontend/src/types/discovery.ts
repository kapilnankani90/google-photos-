/**
 * Core Type Definitions for Google Photos Discovery Engine (Deliverable 1).
 * 
 * Strict alignment with:
 * - part1_memory_representation_schema_v2.md (Locked V2 Schema)
 * - part1_discovery_engine_implementation_spec.md (Section 18.2)
 * - backend/app/retrieval/models.py
 */

export type TemporalNature = 
  | "COARSE_YEAR_ERA" 
  | "RELATIVE_OFFSET" 
  | "SEASON_EVENT_BOUND" 
  | "EXACT_MONTH_YEAR";

export interface PersonConcept {
  role: string;
  count?: number | null;
  attributes: string[];
  possessive?: string | null;
}

export interface EventConcept {
  event_name: string;
  sub_event?: string | null;
}

export interface ObjectConcept {
  name: string;
  attributes: string[];
  possessive?: string | null;
}

export interface TemporalConcept {
  raw_time_expression: string;
  coarse_value?: string | null;
  temporal_nature?: TemporalNature | null;
}

/** Locked Layer 2 Memory Representation */
export interface V2MemoryRepresentation {
  raw_input: string;
  people: PersonConcept[];
  events?: EventConcept | null;
  objects: ObjectConcept[];
  actions: string[];
  temporal?: TemporalConcept | null;
  literal_text: string[];
  spatial_setting?: string | null;
}

/** Derived Search Primitives (Stage 3) */
export interface RetrievalSignals {
  visual_entities: string[];
  bound_attributes: Record<string, unknown>[];
  demographic_proxies?: Record<string, unknown>[];
  action_signals: string[];
  temporal_interval?: { start_utc?: string; end_utc?: string } | null;
  literal_text_tokens: string[];
  spatial_cues: string[];
  search_query_terms?: string[];
}

/** Candidate Score Breakdown (Stage 5) */
export interface ScoreBreakdown {
  base_rrf: number;
  bound_bonus: number;
  distractor_penalty: number;
}

/** Candidate Ranking Result (Stage 6) */
export interface CandidateResult {
  candidate_id: string;
  chunk_id?: string | null;
  case_id?: string | null;
  chunk_type?: string | null;
  content: string;
  rank: number;
  score: number;
  score_breakdown: ScoreBreakdown;
  retrieval_paths: string[];
  metadata: {
    external_id?: string | null;
    methodology?: string | null;
    rating?: number | null;
    failure_mode?: string | null;
    category_tags?: string[] | null;
    evidence_type?: string | null;
    case_created_at?: string | null;
    [key: string]: unknown;
  };
}

/** Locked Section 18.2 Discovery Engine Response */
export interface DiscoveryResponse {
  raw_input: string;
  v2_frame: V2MemoryRepresentation;
  retrieval_signals: RetrievalSignals;
  coverage_status: string;
  controlled_recovery_triggered: boolean;
  candidate_pool_size: number;
  results: CandidateResult[];
}

/** API Request Payload */
export interface DiscoveryRequestPayload {
  raw_input?: string;
  query?: string | V2MemoryRepresentation;
  v2_representation?: V2MemoryRepresentation;
  filters?: {
    source_type?: string;
    methodology?: string;
    evidence_type?: string;
    failure_mode?: string;
    rating?: number;
    category_tags?: string[];
    signal_strength?: string;
    start_date?: string;
    end_date?: string;
  };
  top_k?: number;
  enable_recovery?: boolean;
}

/** Canonical Benchmark Case */
export interface CanonicalCase {
  id: string;
  title: string;
  query: string;
  category: string;
  description: string;
}

/** Research Grounded Synthesis Response (Subsystem B scaffold) */
export interface ClaimCitation {
  claim_text: string;
  cited_case_id: string;
  verbatim_quote: string;
  relationship: "SUPPORTS" | "QUALIFIES" | "CONTRADICTS" | "INSUFFICIENT";
  verification_status?: "VERIFIED_EXACT" | "VERIFIED_FUZZY" | "UNVERIFIED" | "FAILED";
  verification_score?: number;
}

export interface ResearchSynthesisResponse {
  query: string;
  grounding_status: "FULLY_GROUNDED" | "QUALIFIED" | "INSUFFICIENT_EVIDENCE";
  synthesis: string;
  cited_cases: ClaimCitation[];
  contradictions: unknown[] | null;
}
