/**
 * Core Type Definitions for Google Photos Discovery Engine (Part 1).
 * 
 * Strict alignment with:
 * - part1_memory_representation_schema_v2.md (Locked V2 Schema)
 * - part1_discovery_engine_implementation_spec.md
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

/** Derived Search Primitives (Scaffold for Step 4) */
export interface RetrievalSignals {
  visual_entities: string[];
  bound_attributes: Record<string, unknown>[];
  demographic_proxies: Record<string, unknown>[];
  action_signals: string[];
  temporal_interval?: { start_utc?: string; end_utc?: string } | null;
  literal_text_tokens: string[];
  spatial_cues: string[];
}

/** Candidate Ranking Result (Scaffold for Step 6) */
export interface CandidateResult {
  candidate_id: string;
  rank: number;
  score: number;
  score_breakdown: {
    base_rrf: number;
    bound_bonus: number;
    distractor_penalty: number;
  };
  retrieval_paths: string[];
  metadata: Record<string, unknown>;
}

/** Research Grounded Synthesis Response (Scaffold for Step 7) */
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
