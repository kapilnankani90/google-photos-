-- ==============================================================================
-- Migration: 001_initial_schema.sql
-- Part 1 — Google Photos Discovery Engine Database Schema
-- Supabase PostgreSQL 15+ with pgvector
-- Engineering Source of Truth: part1_discovery_engine_implementation_spec.md
-- ==============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 1. Sources Table (Provenance Tracking)
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('PLAY_STORE', 'REDDIT', 'USER_INTERVIEW')),
    name VARCHAR(255) NOT NULL,
    document_reference TEXT,
    provenance_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Evidence Cases Table (Master Qualitative Research Repository)
CREATE TABLE evidence_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    external_id VARCHAR(100) NOT NULL UNIQUE, -- e.g., 'rev-user-a', 'reddit-raw-003', 'interview-c01-s01'
    raw_text TEXT NOT NULL,
    user_debrief TEXT,
    app_version VARCHAR(50),
    rating INT CHECK (rating BETWEEN 1 AND 5),
    methodology VARCHAR(50) NOT NULL CHECK (methodology IN ('UNSOLICITED_PUBLIC', 'PROMPTED_INTERVIEW')),
    evidence_type VARCHAR(50) NOT NULL CHECK (evidence_type IN ('FAILURE', 'SUCCESS', 'NEUTRAL')),
    failure_mode VARCHAR(100), -- e.g., 'CONTEXT_NOT_UNDERSTOOD', 'INCOMPLETE_RESULTS', 'VERNACULAR_FAILURE'
    job_to_be_done TEXT,
    signal_strength VARCHAR(20) DEFAULT 'MEDIUM' CHECK (signal_strength IN ('LOW', 'MEDIUM', 'HIGH')),
    category_tags TEXT[] DEFAULT '{}',
    structured_situation JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evidence_source ON evidence_cases(source_id);
CREATE INDEX idx_evidence_methodology ON evidence_cases(methodology);
CREATE INDEX idx_evidence_failure_mode ON evidence_cases(failure_mode);
CREATE INDEX idx_evidence_category ON evidence_cases USING GIN(category_tags);

-- 3. Evidence Chunks Table (Fine-Grained Retrieval & Local Embeddings)
CREATE TABLE evidence_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evidence_case_id UUID NOT NULL REFERENCES evidence_cases(id) ON DELETE CASCADE,
    chunk_type VARCHAR(50) NOT NULL CHECK (chunk_type IN ('RAW_QUOTE', 'DEBRIEF', 'SITUATION_SUMMARY', 'JTBD')),
    content TEXT NOT NULL,
    embedding VECTOR(384) NOT NULL, -- 384 dimensions matching benchmark candidates (multilingual-e5-small / MiniLM-L12-v2)
    search_vector TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- HNSW Vector index for fast approximate nearest neighbor search
CREATE INDEX idx_chunks_embedding ON evidence_chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- GIN Full-Text Search index
CREATE INDEX idx_chunks_fts ON evidence_chunks USING GIN(search_vector);

-- 4. V2 Memory Representations Table (Structured Memory Frames matching Locked V2 Schema)
CREATE TABLE memory_representations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evidence_case_id UUID REFERENCES evidence_cases(id) ON DELETE SET NULL,
    raw_input TEXT NOT NULL,
    people JSONB DEFAULT '[]'::jsonb,
    events JSONB DEFAULT NULL, -- Object in locked V2 schema (event_name, sub_event)
    objects JSONB DEFAULT '[]'::jsonb,
    actions JSONB DEFAULT '[]'::jsonb,
    temporal JSONB DEFAULT NULL, -- Object in locked V2 schema (raw_time_expression, coarse_value, temporal_nature)
    literal_text JSONB DEFAULT '[]'::jsonb,
    spatial_setting TEXT, -- String in locked V2 schema
    is_benchmark_case BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 5. Retrieval Signals Table (Interpreted Query Vectors & Primitives)
CREATE TABLE retrieval_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    memory_representation_id UUID NOT NULL REFERENCES memory_representations(id) ON DELETE CASCADE,
    visual_entity_signals JSONB DEFAULT '[]'::jsonb,
    bound_attribute_signals JSONB DEFAULT '[]'::jsonb,
    relational_signals JSONB DEFAULT '[]'::jsonb,
    action_signals JSONB DEFAULT '[]'::jsonb,
    temporal_constraints JSONB DEFAULT '{}'::jsonb,
    literal_text_signals JSONB DEFAULT '[]'::jsonb,
    spatial_signals JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 6. Research Queries & Grounded Syntheses Table (Audit & Traceability)
CREATE TABLE research_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_text TEXT NOT NULL,
    v2_frame JSONB NOT NULL,
    signals JSONB NOT NULL,
    synthesis_text TEXT NOT NULL,
    grounding_status VARCHAR(50) NOT NULL CHECK (grounding_status IN ('FULLY_GROUNDED', 'QUALIFIED', 'INSUFFICIENT_EVIDENCE')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. Claim Citations Table (Verifiable Link from Claim to Evidence Case with Quote Verification)
CREATE TABLE claim_citations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID NOT NULL REFERENCES research_queries(id) ON DELETE CASCADE,
    evidence_case_id UUID NOT NULL REFERENCES evidence_cases(id) ON DELETE CASCADE,
    claim_statement TEXT NOT NULL,
    relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN ('SUPPORTS', 'QUALIFIES', 'CONTRADICTS', 'INSUFFICIENT')),
    quote_snippet TEXT NOT NULL, -- Verbatim quote verified against raw text/debrief
    verification_status VARCHAR(50) NOT NULL DEFAULT 'UNVERIFIED' CHECK (verification_status IN ('VERIFIED_EXACT', 'VERIFIED_FUZZY', 'UNVERIFIED', 'FAILED')),
    verification_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_citations_query ON claim_citations(query_id);
CREATE INDEX idx_citations_case ON claim_citations(evidence_case_id);

-- 8. Benchmark Photo Candidates Table (Subsystem A: Algorithmic Discovery Core Media Records)
CREATE TABLE benchmark_candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id VARCHAR(100) NOT NULL UNIQUE, -- e.g., 'c1_tgt_family_5sisters'
    case_id VARCHAR(50) NOT NULL, -- e.g., 'case_1'
    is_target BOOLEAN NOT NULL DEFAULT FALSE,
    caption TEXT,
    visual_entities TEXT[] DEFAULT '{}',
    bound_attributes JSONB DEFAULT '[]'::jsonb,
    literal_ocr_text TEXT[] DEFAULT '{}',
    demographic_primitives JSONB DEFAULT '{}'::jsonb,
    event_context VARCHAR(100),
    timestamp_utc TIMESTAMPTZ,
    location_label VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_candidates_case ON benchmark_candidates(case_id);

-- 9. Experiment Regression Runs Table
CREATE TABLE experiment_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    commit_hash VARCHAR(40),
    strategy_a_recall FLOAT NOT NULL,
    strategy_a_p1 FLOAT NOT NULL,
    strategy_b_recall FLOAT NOT NULL,
    strategy_b_p1 FLOAT NOT NULL,
    zero_result_count INT NOT NULL,
    passed_parity BOOLEAN NOT NULL,
    full_output JSONB NOT NULL
);
