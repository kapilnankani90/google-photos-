# Part 1 — Discovery Engine Implementation Specification

---

## 1. Executive Summary

### 1.1 Purpose of This Specification
This document establishes the concrete engineering and deployment contract to translate the locked conceptual architecture of **Part 1: Build an AI-Powered Discovery Engine** into a functioning, production-ready, interactive software system. 

The conceptual and experimental foundations of Part 1 are complete and locked across:
- [part1_memory_representation_schema_v2.md](file:///d:/graduation%20project%203/part1_memory_representation_schema_v2.md) (Locked V2 Memory Schema)
- [part1_discovery_engine_architecture_final.md](file:///d:/graduation%20project%203/part1_discovery_engine_architecture_final.md) (Locked 7-Stage Conceptual Pipeline)
- [part1_discovery_engine_operating_spec_final.md](file:///d:/graduation%20project%203/part1_discovery_engine_operating_spec_final.md) (Locked Operational Traces)
- [part1_discovery_engine_experimental_spec.md](file:///d:/graduation%20project%203/part1_discovery_engine_experimental_spec.md) (Locked Experimental Protocol)
- [part1_experiment_results.json](file:///d:/graduation%20project%203/part1_experiment_results.json) (Locked Empirical Baseline & Results)
- [part1_experimental_findings.md](file:///d:/graduation%20project%203/part1_experimental_findings.md) (Locked Experimental Analysis)

This specification does **not** redesign the Discovery Engine, reopen the memory schema, invent new user research, or jump ahead to the consumer-facing Memory Search product (Part 5). Instead, it defines the exact technical implementation required to deploy the **Discovery Engine as an Interactive Research & Evidence Discovery System** that indexes empirical user evidence, runs multi-path hybrid retrieval, evaluates coverage and compositional matching, and generates strictly grounded research insights with end-to-end evidence provenance.

### 1.2 Core Project Anchor
All components in this specification are directly governed by the assignment's strategic objective:

$$\mathbf{PROJECT\ ANCHOR:}\ \text{Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching.}$$

In the software system specified here, this anchor is operationalized across two distinct, complementary subsystems with clearly delineated responsibilities:
1. **Subsystem A — The Algorithmic Discovery Engine Core (Photo Retrieval Engine):** The 7-stage deterministic retrieval pipeline (Interpretation $\rightarrow$ Signal Generation $\rightarrow$ Multi-Path Discovery $\rightarrow$ Coverage Checking $\rightarrow$ Controlled Recovery $\rightarrow$ Compositional Matching $\rightarrow$ Result Organization) that operates on photo media metadata and benchmark candidates to solve the photo retrieval problem directly.
2. **Subsystem B — The Qualitative Research Evidence RAG Console (Research Intelligence System):** A server-side RAG engine and exploration console that ingests, indexes, and analyzes the empirical research corpus (Play Store reviews, Reddit threads, 1:1 user interview transcripts) to explain *why* users fail, verify failure modes, track cross-source contradictions, and synthesize grounded research insights.

**Relationship Between Subsystems:** Subsystem B is the research and diagnostics engine that surfaced the failure modes (kinship gaps, vernacular particles, attribute flooding, temporal rigidity) that Subsystem A was engineered to resolve. They share the V2 representation format and retrieval principles, but operate on different data domains (photo media records vs. qualitative research evidence cases).

---

## 2. Artifact-to-Implementation Mapping

The table below audits the existing Part 1 artifacts and defines their translation into concrete software components:

| Locked Part 1 Artifact | Conceptual Responsibility in Part 1 | Concrete Software Component in Implementation | Data Consumed | Data Produced | Deterministic vs. LLM | Testing & Verification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `part1_memory_representation_schema_v2.md` | Informational structure of human memory (Layers 1 & 2) | Pydantic model (`V2MemoryRepresentation`) & PostgreSQL JSONB column | Raw query string (`raw_input`) | Validated V2 JSON object | Deterministic rule engine with fallback to Gemini structured parser | Unit tests against schema validation; Pydantic model round-trip tests |
| `part1_discovery_engine_architecture_final.md` (Stages 1–3) | Intent interpretation & Retrieval signal generation | `MemoryInterpreter` & `SignalGenerator` Python modules | `raw_input` & V2 Memory Frame | Coordinated `RetrievalSignals` object | Rule-based parser for known vernacular/temporal markers; Gemini for open-domain intent parsing | Case-based integration tests verifying signal extraction for 8 canonical cases |
| `part1_discovery_engine_architecture_final.md` (Stage 4) | Multi-path discovery, coverage check, controlled recovery | `MultiPathRetriever`, `CoverageChecker`, `ControlledRecovery` | `RetrievalSignals`, PostgreSQL pgvector, and FTS indexes | `CandidatePool` (ranked candidates with path metadata) | **100% Deterministic** (SQL, pgvector cosine, FTS ranking, rule-based coverage heuristics) | Regression tests against `part1_experimental_benchmark.json` |
| `part1_discovery_engine_architecture_final.md` (Stage 5) | Compositional matching & multi-clue scoring | `CompositionalScorer` | Candidate metadata & V2 Memory Frame | Scored & re-ranked candidates with score breakdowns | **100% Deterministic** (Binding rules, penalty multipliers, tie-breakers) | Parity tests verifying candidate ranks against `part1_experiment_results.json` |
| `part1_discovery_engine_architecture_final.md` (Stage 6) | Contextual result organization | `ResultOrganizer` | Scored candidate pool | Grouped/clustered candidate timelines | **100% Deterministic** (Temporal clustering, session boundary grouping) | Day-coverage and cluster-cohesion unit tests (Case 7 & Case 8) |
| `part1_discovery_engine_operating_spec_final.md` | End-to-end trace behaviors across 8 canonical cases | System integration test suite (`tests/test_operational_traces.py`) | 8 representative query inputs | End-to-end trace logs matching operating spec | Pipeline orchestration | Snapshot tests asserting exact trace state transitions |
| `part1_experimental_benchmark.json` & `part1_experiment_results.json` | Ground truth test benchmark (65 candidate records) | Regression test fixture & seed data (`tests/data/benchmark.json`) | Benchmark queries and candidates | Recall@K, Precision@1, Zero-Result counts | Deterministic execution | Automated CI regression verifying +35% recall gain and 0 zero-result cases |
| `cross_source_synthesis.md` & Evidence Datasets | Master project evidence corpus across 3 sources (245 Play Store, 38 Reddit, 25 Interviews) | Database seed migration & Ingestion pipeline (`scripts/ingest_evidence.py`) | Master JSON evidence files | Normalized DB records in `evidence_cases` & `sources` | Deterministic ETL parser | Manifest-driven ingestion integrity tests; source-count and foreign-key validation |

---

## 3. System Architecture

### 3.1 High-Level Architecture Diagram

```mermaid
flowchart TB
    subgraph Client ["Client Layer (Vercel)"]
        UI["Next.js / React Web App<br/>• Interactive Research Console<br/>• Multi-Path Retrieval Playground<br/>• Grounded Insight Explorer<br/>• Regression Test Monitor"]
    end

    subgraph Backend ["Backend API Layer (Railway)"]
        API["FastAPI Application"]
        
        subgraph Pipeline ["Discovery Engine Pipeline"]
            S2["Stage 2: Memory Interpreter<br/>(Rule Parser / Gemini Fallback)"]
            S3["Stage 3: Retrieval Signal Generator<br/>(Deterministic Signal Derivation)"]
            S4A["Stage 4: Multi-Path Retriever<br/>• FTS (tsvector)<br/>• Vector (pgvector)<br/>• Structured Metadata"]
            S4B["Stage 4: Candidate Coverage Checker<br/>(Threshold & Diversity Heuristics)"]
            S4C["Stage 4: Controlled Recovery<br/>(Path Broadening Engine)"]
            S5["Stage 5: Compositional Scorer<br/>(Entity-Attribute Binding)"]
            S6["Stage 6: Result Organizer<br/>(Temporal & Event Clustering)"]
        end
        
        subgraph RAG ["Grounded Research Insight Engine"]
            RAG_Prompt["Prompt Formatter<br/>(Zero-Hallucination Template)"]
            RAG_Exec["Gemini 2.5 Flash Client<br/>(Strictly Constrained to Context)"]
            Claim_Val["Claim & Provenance Validator<br/>(Citation Verifier)"]
        end

        subgraph LocalModel ["Local Embedding Service (Railway CPU)"]
            Embedder["sentence-transformers<br/>384-dim Model (Benchmark Selected Candidate)"]
        end
    end

    subgraph Data ["Data & Storage Layer (Supabase)"]
        DB[(PostgreSQL 15+)]
        PGV["pgvector Extension<br/>(HNSW Cosine Index)"]
        FTS["PostgreSQL FTS<br/>(GIN Indexes on tsvector)"]
        DB --- PGV
        DB --- FTS
    end

    subgraph External ["External AI Services"]
        GeminiAPI["Google Gemini API<br/>(Server-Side API Key)"]
    end

    UI -->|HTTPS / REST| API
    API --> Pipeline
    S2 --> S3
    S3 --> S4A
    S4A <-->|SQL Queries / Embeddings| DB
    S4A --> S4B
    S4B -- Insufficient --> S4C
    S4C --> S4A
    S4B -- Sufficient --> S5
    S5 --> S6
    
    API --> RAG
    RAG -->|Fetch Evidence Chunks| DB
    RAG_Prompt --> RAG_Exec
    RAG_Exec <-->|API Calls| GeminiAPI
    RAG_Exec --> Claim_Val
    
    Pipeline <-->|Compute Embeddings| Embedder
    RAG <-->|Compute Query Embeddings| Embedder
```

### 3.2 Architectural Invariants
1. **Server-Side AI Isolation:** The client browser never communicates directly with the Gemini API or the database. All AI interactions and database transactions are mediated by the FastAPI backend.
2. **Zero Paid Embedding API Dependency:** All text embeddings are computed locally on the Railway container using a lightweight, open-source transformer model.
3. **Decoupled Search Modalities:** Lexical search (PostgreSQL FTS), semantic search (`pgvector`), and relational attribute filtering execute as independent candidate streams before being merged into the unified candidate pool.
4. **Strict Grounding Boundary:** Gemini is utilized exclusively for:
   - Natural language memory parsing (when deterministic rules encounter ambiguous open-domain queries).
   - Synthesizing research insights across retrieved database evidence records.
   Gemini is **never** permitted to generate claims or retrieve information outside the explicitly supplied database context.

---

## 4. Database Schema

The database is hosted on Supabase PostgreSQL (version 15+) with `pgvector` enabled.

```mermaid
erDiagram
    SOURCES ||--o{ EVIDENCE_CASES : "provides"
    EVIDENCE_CASES ||--o{ EVIDENCE_CHUNKS : "chunked_into"
    EVIDENCE_CASES ||--o| MEMORY_REPRESENTATIONS : "modeled_as"
    MEMORY_REPRESENTATIONS ||--o| RETRIEVAL_SIGNALS : "generates"
    RESEARCH_QUERIES ||--o{ QUERY_RETRIEVAL_RESULTS : "retrieves"
    EVIDENCE_CASES ||--o{ QUERY_RETRIEVAL_RESULTS : "surfaced_in"
    RESEARCH_QUERIES ||--o{ CLAIM_CITATIONS : "supports"
    EVIDENCE_CASES ||--o{ CLAIM_CITATIONS : "cited_by"
    EXPERIMENT_RUNS ||--o{ EXPERIMENT_CASE_RESULTS : "evaluates"

    SOURCES {
        uuid id PK
        varchar source_type
        varchar name
        text document_reference
        jsonb provenance_metadata
        timestamptz created_at
    }

    EVIDENCE_CASES {
        uuid id PK
        uuid source_id FK
        varchar external_id
        text raw_text
        text user_debrief
        varchar app_version
        int rating
        varchar methodology
        varchar evidence_type
        varchar failure_mode
        text job_to_be_done
        varchar signal_strength
        text[] category_tags
        jsonb structured_situation
        timestamptz created_at
    }

    EVIDENCE_CHUNKS {
        uuid id PK
        uuid evidence_case_id FK
        varchar chunk_type
        text content
        vector embedding
        tsvector search_vector
        timestamptz created_at
    }

    MEMORY_REPRESENTATIONS {
        uuid id PK
        uuid evidence_case_id FK
        text raw_input
        jsonb people
        jsonb events
        jsonb objects
        jsonb actions
        jsonb temporal
        jsonb literal_text
        jsonb spatial_setting
        boolean is_benchmark_case
        timestamptz created_at
    }

    RETRIEVAL_SIGNALS {
        uuid id PK
        uuid memory_representation_id FK
        jsonb visual_entity_signals
        jsonb bound_attribute_signals
        jsonb relational_signals
        jsonb action_signals
        jsonb temporal_constraints
        jsonb literal_text_signals
        jsonb spatial_signals
        timestamptz created_at
    }

    RESEARCH_QUERIES {
        uuid id PK
        text query_text
        jsonb v2_frame
        jsonb signals
        text synthesis_text
        varchar grounding_status
        timestamptz created_at
    }

    CLAIM_CITATIONS {
        uuid id PK
        uuid query_id FK
        uuid evidence_case_id FK
        text claim_statement
        varchar relationship_type
        text quote_snippet
        timestamptz created_at
    }
```

### 4.1 SQL DDL Definition

```sql
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
```

---

## 5. Evidence Ingestion

### 5.1 Master Project Evidence Corpus Scope
The primary ingestion architecture supports the full project evidence corpus across three research streams, preserving the fundamental methodological boundary between unsolicited consumer feedback and prompted qualitative observations:

| Source Stream | Methodology Type | Master Corpus Scope | Source Description & Ingestion Strategy |
| :--- | :--- | :--- | :--- |
| **Google Play Store** | `UNSOLICITED_PUBLIC` | **245 Evidence Cases** | Unsolicited public consumer reviews. Ingests failure modes, app ratings, JTBD, and raw review excerpts. *(Note: Historical subsets such as the 23-item pristine or 50-item exploratory batches are retained only as optional curated subsets; the primary architecture ingests the full 245 cases).* |
| **Reddit r/googlephotos** | `UNSOLICITED_PUBLIC` | **38 Evidence Cases** | Unsolicited power-user forum discussions (50k+ photo libraries, cross-device sync, OCR tracking, truncation failure modes). Ingests full thread context and situation metadata. |
| **1:1 User Interviews** | `PROMPTED_INTERVIEW` | **25 Retrieval Episodes** | Prompted task-based qualitative testing across 6 participants (Episodes 01–25). Ingests verbatim queries, scroll depths, ranking sections, and debrief reflections. |

**Total Authoritative Evidence Corpus:** $245 + 38 + 25 = 308$ master evidence cases.

### 5.2 Ingestion Script Architecture & Manifest-Driven Validation
A deterministic ingestion worker `scripts/ingest_evidence.py` coordinates the ingestion process:
1. **Source Registration:** Creates 3 canonical entries in `sources` table (`PLAY_STORE`, `REDDIT`, `USER_INTERVIEW`) if not present.
2. **Idempotent Record Upsert:** Upserts each record into `evidence_cases` keyed by `external_id`.
3. **Chunking & Vector Generation:** Chunks each record into discrete textual views (`RAW_QUOTE`, `DEBRIEF`, `SITUATION_SUMMARY`), invokes the local embedding service, and inserts chunks into `evidence_chunks` with precomputed vectors.
4. **Manifest-Driven Validation:** Ingestion is governed by a declarative manifest (`config/ingestion_manifest.json`). The validator checks that each configured source dataset parses without schema errors, that zero required fields are null, and that the ingested record counts satisfy the authoritative project corpus thresholds ($\ge 245$ Play Store cases, $\ge 38$ Reddit cases, and $\ge 25$ interview episodes, totaling 308 master records). No outdated count assumptions (such as 113) are permitted.

---

## 6. Evidence Normalization

### 6.1 Preserving Methodological Distinctions
Unsolicited feedback (Play Store, Reddit) and prompted observations (Interviews) must never be flattened into an undifferentiated pool. The database strictly enforces the `methodology` column:
- **`UNSOLICITED_PUBLIC`:** Represents spontaneous user complaints occurring in the wild. High authenticity of natural user pain; low visibility into exact gallery state or prompt sequence.
- **`PROMPTED_INTERVIEW`:** Represents controlled, observed behavioral tasks. Complete visibility into attempted search queries, candidate scroll depth, ranking section, and post-task debrief reflections.

### 6.2 Standardized Failure Mode Taxonomy
All ingested records are normalized to a unified, controlled taxonomy of retrieval failure modes:
1. `KINSHIP_VOCABULARY_GAP`: Social roles (`sister`, `cousin`) fail to match demographic index tags.
2. `VERNACULAR_FAILURE`: Grammatical particles (e.g., Hinglish `ki`, `wali`, `ke sath`) cause zero-result screens.
3. `UNBOUND_ATTRIBUTE_FLOOD`: Independent attribute matching floods results (e.g., `yellow` matches walls instead of `suit`).
4. `PREMATURE_TRUNCATION`: System caps candidate returns arbitrarily (e.g., 6 of 400 photos).
5. `LITERAL_OCR_DROPOUT`: Alphanumeric text inside images is ignored or treated as a conversational command.
6. `TEMPORAL_RIGIDITY`: System rejects approximate or relative time offsets (`before covid`, `4 years ago`).
7. `SESSION_TRUNCATION`: Photos from multi-day episodes are fragmented or lost across date gaps.
8. `CONTEXT_COLLAPSE`: Chronological or event clustering is stripped, disorienting the user.

---

## 7. V2 Memory Representation Implementation

### 7.1 Pydantic Model Definition (Matching Locked V2 JSON Schema Exactly)
The locked V2 Schema defined in `part1_memory_representation_schema_v2.md` is implemented in Python using Pydantic v2 with exact adherence to field names, data types, required fields, and `additionalProperties: false`:

```python
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict

class PersonConcept(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: str = Field(..., description="Kinship or social role (e.g., sister, cousin, brother, maid, watchman, colleague).")
    count: Optional[int] = Field(None, description="Explicit group count if recalled (e.g., 5 in '5 sisters', 2 in 'two ladies').")
    attributes: List[str] = Field(default_factory=list, description="Descriptive visual or clothing modifiers bound to this person/group (e.g., ['yellow suit'], ['blue outfit']).")
    possessive: Optional[str] = Field(None, description="Possessive marker if expressed (e.g., 'my', 'our').")

class EventConcept(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_name: str = Field(..., description="Primary event name (e.g., wedding, diwali, farewell, birthday, holi, engagement).")
    sub_event: Optional[str] = Field(None, description="Optional specific ritual or sub-phase (e.g., haldi, rehearsal, farewell lunch).")

class ObjectConcept(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(..., description="Name of physical object or document (e.g., cake, bike, papaya, ring box, diya, truck, boarding pass).")
    attributes: List[str] = Field(default_factory=list, description="Descriptive visual modifiers bound directly to this object (e.g., ['white'] for bike, ['yellow'] for truck, ['steel plate'] for cake).")
    possessive: Optional[str] = Field(None, description="Possessive marker if expressed (e.g., 'my', 'our').")

class TemporalConcept(BaseModel):
    model_config = ConfigDict(extra="forbid")
    raw_time_expression: str = Field(..., description="Verbatim temporal phrase (e.g., 'around 4 years ago', '2021', 'July 2016', 'Holi 2020').")
    coarse_value: Optional[str] = Field(None, description="Extracted year or coarse era if identifiable (e.g., '2021', '2016', '4 years ago').")
    temporal_nature: Optional[Literal["COARSE_YEAR_ERA", "RELATIVE_OFFSET", "SEASON_EVENT_BOUND", "EXACT_MONTH_YEAR"]] = Field(
        None, description="Broad characterization of the temporal anchor without imposing rigid timestamps."
    )

class V2MemoryRepresentation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    raw_input: str = Field(..., description="Verbatim user query or natural-language memory description exactly as provided.")
    people: List[PersonConcept] = Field(default_factory=list, description="People recalled by social, familial, or occupational role.")
    events: Optional[EventConcept] = Field(None, description="Milestone event, cultural celebration, or social occasion.")
    objects: List[ObjectConcept] = Field(default_factory=list, description="Salient physical props, vehicles, food preparations, or utility documents.")
    actions: List[str] = Field(default_factory=list, description="Dynamic activities, physical sports, interactions, or bodily poses.")
    temporal: Optional[TemporalConcept] = Field(None, description="Coarse calendar, relative elapsed, or specific temporal anchor.")
    literal_text: List[str] = Field(default_factory=list, description="Literal alphanumeric text remembered as physically printed on an object, document, or screen.")
    spatial_setting: Optional[str] = Field(None, description="Broad geographic destination, landscape type, or architectural boundary (e.g., 'mountain', 'beach', 'gate', 'rohtang', 'Mussoorie').")
```

### 7.2 Memory Interpretation Execution Flow
```mermaid
flowchart LR
    Input["Raw User Expression"] --> Clean["Sanitize & Detect Language/Vernacular"]
    Clean --> RuleEngine{"Matches Deterministic Rule?"}
    RuleEngine -- Yes --> RuleParse["Deterministic V2 Parser<br/>(Hinglish particles, exact offsets, canonical roles)"]
    RuleEngine -- No --> LLMParse["Gemini Structured Parser<br/>(Few-Shot Prompt constrained to V2 Schema)"]
    RuleParse --> Validate["Pydantic Schema Validation"]
    LLMParse --> Validate
    Validate --> Output["Validated V2 Memory Frame"]
```

---

## 8. Retrieval Signal Generation

### 8.1 Signal Derivation Logic
The Retrieval Signal Generation layer derives actionable database search probes from the interpreted V2 Memory Frame:

```python
class RetrievalSignals(BaseModel):
    visual_entities: List[str] = Field(default_factory=list, description="Direct entity nouns for visual/object lookup")
    bound_attributes: List[dict] = Field(default_factory=list, description="Entity-modifier pairs for compositional ranking")
    demographic_proxies: List[dict] = Field(default_factory=list, description="Demographic cluster primitives derived from kinship")
    action_signals: List[str] = Field(default_factory=list, description="High-specificity physical verbs")
    temporal_interval: Optional[dict] = Field(None, description="Start/End timestamps derived from coarse expressions")
    literal_text_tokens: List[str] = Field(default_factory=list, description="Verbatim tokens for OCR matching")
    spatial_cues: List[str] = Field(default_factory=list, description="Landscape and environment terms")
```

### 8.2 Permanent Implementation Rules (Generalized Engine Mechanisms)
The engine executes four permanent, generalized signal derivation mechanisms:
1. **Compositional Entity-Attribute Binding:** Visual modifiers (`attributes`) are bound directly to their qualifying entity (`objects` or `people`), preventing uncoordinated token cross-talk during candidate scoring.
2. **Vernacular Particle Stripping:** Grammatical code-mixed particles (e.g., Hinglish `ki`, `ke`, `wali`, `wala`, `ka`, `se`, `photo`, `pic`) are programmatically identified and isolated from core semantic nouns (`visual_entities`) while preserving `raw_input` untouched.
3. **Coarse & Relative Temporal Calculation:** Coarse calendar intervals (e.g., year `"2021"` $\rightarrow$ `2021-01-01` to `2021-12-31`) and relative offsets (e.g., `"around 4 years ago"`) are dynamically computed relative to reference system time.
4. **Literal OCR Segregation:** Alphanumeric strings, document identification numbers, and printed snippets are routed exclusively to `literal_text_tokens`, preventing literal print text from corrupting semantic visual embeddings.

### 8.3 Experimental Benchmark Retrieval Proxies (Test Fixtures & Handlers)
> [!IMPORTANT]
> **Strict Architectural Separation:**
> As established in [part1_discovery_engine_architecture_final.md](file:///d:/graduation%20project%203/part1_discovery_engine_architecture_final.md), the Discovery Engine **does not hardcode global domain mappings** (such as permanently equating `"sister"` with `"female/woman/girl"`).
> 
> The specific mappings utilized in the Part 1 experiment—such as translating `"5 sisters"` into demographic primitives (`group_count: 5, apparent_gender: female`) or anchoring `"before covid"` to pre-March 2020—are **experimental test fixtures and benchmark handlers**. They are implemented in `tests/fixtures/benchmark_handlers.py` to evaluate candidate recovery under the controlled benchmark, and must remain strictly isolated from permanent, open-domain production rules.

---

## 9. Embedding Strategy

### 9.1 Embedding Selection as a Deployment Benchmark Decision
Rather than blindly locking a model without empirical container validation, the embedding model selection is treated as an **empirical deployment benchmark decision** to be finalized on the Railway production container during Phase 2.

To adhere strictly to the **zero paid embedding API** constraint while supporting code-mixed vernacular queries (e.g., Hinglish) on Railway's 512MB–1GB RAM limits, candidate models are evaluated across six technical dimensions:

| Candidate Model | Dimensions | Model Size (Disk) | Memory Footprint (RAM) | Multilingual / Hinglish Support | Retrieval Quality (MTEB) | Railway Container Feasibility | Deployment Benchmark Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `all-MiniLM-L6-v2` | 384 | ~90 MB | ~250 MB | Very Poor (English only) | Moderate (56.3) | High | **Disqualified:** Fails on Hinglish vernacular queries (`rohtang ki ice`). |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | ~470 MB | ~650 MB | Good (50+ languages) | Moderate (54.1) | High | **Leading Fallback Contender** |
| `intfloat/multilingual-e5-small` | 384 | ~470 MB | ~600 MB | **Excellent (100+ languages, Hindi/Hinglish subwords)** | **High (59.9)** | **Optimal** | **Leading Primary Contender** |
| `BAAI/bge-small-en-v1.5` | 384 | ~130 MB | ~300 MB | Poor (English-optimized) | High (62.1) | High | **Disqualified:** English only. |
| `BAAI/bge-m3` | 1024 | ~2.2 GB | ~2.8 GB | Superior (100+ languages) | Outstanding (64.6) | **Impossible:** Exceeds Railway free-tier RAM limits. |

### 9.2 Railway Deployment Benchmark Protocol
During Phase 2 setup, the deployment script `scripts/benchmark_embeddings.py` benchmarks the top contenders (`multilingual-e5-small` vs. `paraphrase-multilingual-MiniLM-L12-v2`) directly on the target Railway container environment under the following criteria:
1. **Container Memory Headroom:** Container peak RSS must stay $\le 750$ MB under 5 concurrent embedding requests to avoid Railway OOM kills.
2. **Inference Latency:** p95 single-passage embedding latency on Railway shared CPU must remain $\le 350$ ms.
3. **Vernacular Retrieval Accuracy:** Evaluates cosine similarity ranking on representative Hinglish test pairs (`rohtang ki ice` $\leftrightarrow$ snow mountain photos; `durga ke sath picture jo meri maid hai` $\leftrightarrow$ domestic helper captions).

**Initial Benchmark Candidate:** Deploy with `intfloat/multilingual-e5-small` as the initial benchmark candidate configured via `EMBEDDING_MODEL_NAME`. The final embedding model selection remains strictly subject to the empirical Railway deployment benchmark; if container memory telemetry on Railway spikes above 750 MB during load testing, the environment variable switches to `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`. Both models output 384-dimensional vectors, ensuring complete compatibility with the PostgreSQL `VECTOR(384)` schema without requiring database DDL changes.

---

## 10. Hybrid Retrieval Pipeline

The retrieval pipeline executes multi-path discovery without relying on a single monolithic search query.

```mermaid
flowchart TD
    Signals["Retrieval Signals Object"] --> Path1["Path 1: Semantic Vector Search<br/>(pgvector Cosine Sim on Chunks)"]
    Signals --> Path2["Path 2: Full-Text Lexical Search<br/>(tsvector GIN on Case & Chunks)"]
    Signals --> Path3["Path 3: Structured Metadata Filter<br/>(SQL WHERE on Category, Mode, Rating)"]
    Signals --> Path4["Path 4: Temporal Boundary Filter<br/>(SQL Range on created_at / event_dates)"]

    Path1 --> Pool["Unified Candidate Pool Merging"]
    Path2 --> Pool
    Path3 --> Pool
    Path4 --> Pool

    Pool --> ReciprocalRank["Reciprocal Rank Fusion (RRF)<br/>Score = SUM( 1 / (60 + Rank_i) )"]
    ReciprocalRank --> Coverage["Candidate Coverage Check (Stage 4)"]
```

### 10.1 Reciprocal Rank Fusion (RRF) Formulation
Candidates retrieved across semantic vector search and lexical FTS are merged using standard RRF ($k=60$):

$$RRF\_Score(d) = \sum_{m \in \{\text{vector}, \text{lexical}\}} \frac{1}{60 + \text{rank}_m(d)}$$

Where $\text{rank}_m(d)$ is the 1-indexed position of document $d$ in retrieval modality $m$.

---

## 11. Candidate Coverage Checking

### 11.1 Purpose & Responsibility
In accordance with Stage 4 of the locked architecture, Candidate Coverage Checking evaluates whether the initial candidate pool is sufficiently broad, populated, and diverse before advancing to final ranking. It directly addresses the **Premature Truncation Failure Mode** documented in Reddit Cases 4 & 11 (where systems returned only 6 of 400 photos).

### 11.2 Concrete Coverage Heuristics
The candidate pool is evaluated against three deterministic threshold rules:
1. **Minimum Candidate Count Check:**
   - If $|\text{CandidatePool}| < 5$ and the query expressed multi-clue criteria, coverage is marked `INSUFFICIENT_VOLUME`.
2. **Dimension Representation Check:**
   - If the query specified both an entity and a spatial/temporal anchor (e.g., `Shimla` + `snowfall`), but 0 returned candidates contain the spatial or temporal dimension, coverage is marked `INSUFFICIENT_DIMENSIONAL_COVERAGE`.
3. **Temporal Span Check:**
   - If the query is an open person query (e.g., Case 7: `"photos of aarav"`), but all candidates cluster within a single 24-hour window despite library timestamps indicating multiple years, coverage is marked `TRUNCATED_TIME_WINDOW`.

If all checks pass, the pool is marked `COVERAGE_SUFFICIENT` and proceeds directly to Stage 5.

---

## 12. Controlled Recovery

### 12.1 Broadening Mechanisms
When coverage is judged `INSUFFICIENT`, the `ControlledRecovery` module executes controlled path broadening before scoring:

```mermaid
flowchart LR
    Fail["Coverage Insufficient"] --> CheckType{"Failure Cause"}
    CheckType -- "Insufficient Volume" --> B1["Broaden Semantic Threshold<br/>(Cosine distance: 0.70 -> 0.85)"]
    CheckType -- "Missing Dimension" --> B2["Activate Complementary Path<br/>(Fallback to FTS keyword tokenization)"]
    CheckType -- "Truncated Window" --> B3["Expand Temporal Window<br/>(Merge contiguous event days)"]
    
    B1 --> ReQuery["Execute Secondary Retrieval Pass"]
    B2 --> ReQuery
    B3 --> ReQuery
    ReQuery --> Merge["Merge with Initial Pool (Deduplicate)"]
    Merge --> Proceed["Proceed to Stage 5 (Compositional Matching)"]
```

### 12.2 Hard Termination Guardrail
To strictly prevent autonomous infinite loops, Controlled Recovery is restricted to **exactly one secondary retrieval pass** ($MaxRetries = 1$). If the pool remains sparse after the single broadening pass, the engine flags `LOW_CONFIDENCE_POOL` and proceeds to scoring without further loop iterations.

---

## 13. Compositional Matching

### 13.1 Scoring Algorithm
Stage 5 evaluates multi-clue congruence by rewarding candidate photos or evidence cases that satisfy bound relationships rather than scoring disconnected bag-of-words tokens:

$$\text{FinalScore}(c) = S_{\text{base}}(c) + S_{\text{bound}}(c) - P_{\text{distractor}}(c)$$

Where:
- $S_{\text{base}}(c)$: Combined RRF retrieval score from Stage 4.
- $S_{\text{bound}}(c)$: Compositional bonus awarded when qualifying attributes reside on the same entity (e.g., `[bike: white]` awards $+1.5$, whereas a candidate with an unrelated white wall and a red bike receives $0.0$).
- $P_{\text{distractor}}(c)$: Distractor penalty applied to candidates possessing conflicting dominant attributes (e.g., indoor ice cream parlor when the query specifies mountain snow).

### 13.2 Tie-Breaking Rules
Ties are resolved deterministically:
1. Candidate matching explicit OCR text or demographic count exactly is ranked first.
2. If still tied, candidate with closest temporal proximity to the specified milestone is ranked first.
3. If still tied, lower internal database UUID breaks the tie.

---

## 14. RAG + Gemini Architecture

### 14.1 Principle of Strict Grounding & Beyond-ID Validation
When synthesizing research insights across qualitative evidence cases, the Gemini model operates under strict constraints:
- **No External General Knowledge:** Gemini is prohibited from citing consumer search trends or technical facts not present in the supplied database context.
- **Mandatory Quote-Backed Attribution:** Every factual assertion must be attributed to an explicit `cited_case_id` AND must include an exact, extractable `verbatim_quote` from the cited case. Merely attaching a case ID is explicitly treated as insufficient.
- **Zero Hallucination Tolerance:** If the retrieved evidence does not contain facts to answer the user's research query, Gemini is required to output the exact string: `INSUFFICIENT_EVIDENCE`.

### 14.2 Server-Side Structured Prompt Template
The prompt enforces structured JSON output with extractable quotes:

```
You are the Google Photos Research Discovery Assistant.
Your sole job is to answer the user's research question strictly using the provided Evidence Cases.

RULES:
1. Reason ONLY from the evidence text provided below.
2. For EVERY substantive claim, you must provide:
   - "claim_text": Clear factual statement.
   - "cited_case_id": The exact CASE ID from the context.
   - "verbatim_quote": An exact, word-for-word quote snippet from that case supporting the claim.
3. If an evidence case qualifies or contradicts another, explicitly populate the "contradictions" array. Do NOT harmonize contradictions.
4. If the provided evidence is inadequate to answer the question, return:
   {"synthesis_summary": "INSUFFICIENT_EVIDENCE: The empirical research dataset does not contain sufficient cases regarding this query.", "claims": [], "contradictions": []}
5. Never invent user quotes, participant names, or statistics.

OUTPUT FORMAT (JSON ONLY):
{
  "synthesis_summary": "Synthesized insight narrative...",
  "claims": [
    {
      "claim_text": "...",
      "cited_case_id": "...",
      "verbatim_quote": "...",
      "relationship": "SUPPORTS" | "QUALIFIES" | "CONTRADICTS"
    }
  ],
  "contradictions": [ ... ]
}

RETRIEVED EVIDENCE CONTEXT:
{% for case in retrieved_cases %}
---
CASE ID: {{ case.external_id }}
SOURCE: {{ case.source_name }} ({{ case.methodology }})
FAILURE MODE: {{ case.failure_mode }}
RAW EVIDENCE: {{ case.raw_text }}
{% if case.user_debrief %}USER REFLECTION: {{ case.user_debrief }}{% endif %}
---
{% endfor %}

USER RESEARCH QUERY:
{{ user_query }}
```

### 14.3 Gemini Model Selection & Parameters
- **Model:** `gemini-2.5-flash`
- **Temperature:** `0.1` (Minimizes creative variance and hallucinatory elaboration)
- **Top_P:** `0.8`
- **Max Output Tokens:** `1024`
- **Response Format:** `{"type": "json_object"}`

---

## 15. Evidence Traceability & Grounding Verification

### 15.1 Four-Tier Chain of Custody
The system enforces a 4-tier chain of custody for every insight generated:

```
┌────────────────────────────────────────────────────────┐
│                   RESEARCH INSIGHT                     │
│  "Conversational AI search frequently breaks explicit  │
│   date queries and truncates multi-year galleries."    │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                   INDIVIDUAL CLAIM                     │
│  claim_text: "Users searching for exact month/year     │
│   queries received 'can't search using those terms'."  │
│  verbatim_quote: "now it says can't search..."         │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                    EVIDENCE CASE                       │
│  external_id: "reddit-raw-007"                         │
│  methodology: "UNSOLICITED_PUBLIC"                     │
│  failure_mode: "TEMPORAL_RIGIDITY"                     │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                   ORIGINAL SOURCE                      │
│  document_reference: "reddit reviews .docx"            │
│  platform: "r/googlephotos"                            │
│  raw_quote: "I used to search 'July 2016'..."          │
└────────────────────────────────────────────────────────┘
```

### 15.2 Multi-Stage Grounding Verification Pipeline (Server-Side)
To prevent citation fabrication (where an LLM outputs a real case ID but invents the claim content), a deterministic server-side validator (`GroundingValidator`) executes three verification gates on every generated claim before returning it to the user:

1. **Gate 1 — Context Membership Check:** Asserts that `cited_case_id` was explicitly supplied in the retrieved context for the current request.
2. **Gate 2 — Verbatim Quote Matching:** The validator searches the cited case record (`raw_text` and `user_debrief`) for `verbatim_quote`:
   - *Exact Match:* Substring exists verbatim $\rightarrow$ `verification_status = 'VERIFIED_EXACT'` ($score = 1.0$).
   - *Fuzzy Match:* Normalized token overlap $\ge 0.90$ $\rightarrow$ `verification_status = 'VERIFIED_FUZZY'` ($score \ge 0.90$).
   - *Failed:* Quote does not exist in the cited case $\rightarrow$ `verification_status = 'FAILED'`.
3. **Gate 3 — Claim-Quote Consistency Check:** Asserts that `claim_text` shares significant content tokens ($\ge 40\%$ content word overlap) with the verified quote as a heuristic consistency check (rather than formal NLI entailment), preventing real quotes from being attached to unrelated fabricated claims.

**Automated Fallback & Degradation Policy:**
- Claims failing Gate 2 or Gate 3 are stripped from the response and logged as `UNGROUNDED_CLAIM_DROPPED`.
- The overall query `grounding_status` is downgraded:
  - If 100% of claims pass: `FULLY_GROUNDED`.
  - If $\ge 50\%$ pass: `QUALIFIED` (with unverified claims omitted).
  - If $< 50\%$ pass: The entire synthesis is rejected, and the system returns the raw retrieved evidence cases with status `INSUFFICIENT_EVIDENCE`.

---

## 16. Contradiction Handling

Qualitative research evidence frequently exhibits empirical contradictions across differing user environments. The system preserves these contradictions rather than smoothing them away:

### 16.1 Supported Contradiction Categories
1. **Object Proxy vs. Semantic Flooding:**
   - *Case A (Success):* In 1:1 user testing (Episode 01), querying `"Cake"` instantly retrieved a birthday party photo at Rank 1.
   - *Case B (Failure):* In Reddit community evidence (Case 03), querying `"dog"` returned only 6 of 400 photos due to semantic model truncation.
2. **Conversational Helpfulness vs. Command Rejection:**
   - In Play Store reviews, some users praise conversational natural language, whereas power users on Reddit document that conversational AI search rejected explicit month/year queries (`"July 2016"`).

### 16.2 Structured Contradiction Schema
When Gemini detects conflicting evidence among retrieved records, it is required to format the contradiction explicitly:

```json
{
  "contradiction_detected": true,
  "topic": "Keyword Object Search Effectiveness",
  "perspectives": [
    {
      "viewpoint": "Simple physical object queries provide instant zero-friction retrieval",
      "supporting_cases": ["interview-c01-s01"],
      "methodology": "PROMPTED_INTERVIEW",
      "conditions": "Single salient physical prop (cake) acting as an unambiguous proxy for an event."
    },
    {
      "viewpoint": "Broad object keywords cause severe under-retrieval and candidate truncation",
      "supporting_cases": ["reddit-raw-003", "reddit-raw-004"],
      "methodology": "UNSOLICITED_PUBLIC",
      "conditions": "Large multi-year personal libraries with hundreds of target photos."
    }
  ]
}
```

---

## 17. Cross-Source Comparison Engine

The Discovery Engine includes a dedicated comparative analysis module that cross-tabulates findings across the three evidence sources while preserving methodological boundaries:

```
                       CROSS-SOURCE COMPARISON MATRIX
┌──────────────────────┬──────────────────────┬──────────────────────┐
│  PLAY STORE REVIEWS  │  REDDIT DISCUSSIONS  │    1:1 INTERVIEWS    │
│ (Unsolicited Public) │ (Unsolicited Public) │ (Prompted Qualitative│
├──────────────────────┼──────────────────────┼──────────────────────┤
│ • 1★-2★ Reactive Skew│ • Power-User Focus   │ • Observed Protocols │
│ • Face Merging Bugs  │ • 50k+ Photo Scale   │ • High Emotion / Rage│
│ • Update Reversals   │ • Truncation Focus   │ • Vernacular Hinglish│
│ • Timeline Disruption│ • APK Rollback Work  │ • 60% Reformulations │
└──────────────────────┴──────────────────────┴──────────────────────┘
```

The endpoint `GET /api/v1/sources/compare` aggregates failure mode frequencies, signal strengths, and category distributions across each source type without conflating unsolicited complaints with controlled interview outcomes.

---

## 18. API Specification

The backend exposes a clean REST API built with FastAPI:

### 18.1 Endpoints

#### 1. `POST /api/v1/discover`
Executes the full 7-stage Discovery Engine pipeline on a raw memory query.
- **Request Body:**
  ```json
  {
    "raw_input": "rohtang ki ice wali photo",
    "top_k": 10,
    "enable_recovery": true
  }
  ```
- **Response:**
  ```json
  {
    "raw_input": "rohtang ki ice wali photo",
    "v2_frame": { ... },
    "retrieval_signals": { ... },
    "coverage_status": "COVERAGE_SUFFICIENT",
    "controlled_recovery_triggered": false,
    "candidate_pool_size": 18,
    "results": [
      {
        "candidate_id": "c2_tgt_rohtang_snow_jacket",
        "rank": 1,
        "score": 2.5,
        "score_breakdown": {
          "base_rrf": 0.033,
          "bound_bonus": 1.5,
          "distractor_penalty": 0.0
        },
        "retrieval_paths": ["spatial", "visual_entity"],
        "metadata": { ... }
      }
    ]
  }
  ```

#### 2. `POST /api/v1/research/insights`
Retrieves relevant qualitative evidence cases and executes grounded Gemini synthesis.
- **Request Body:**
  ```json
  {
    "research_question": "Why do users fail when searching for family members?",
    "source_filter": ["PLAY_STORE", "REDDIT", "USER_INTERVIEW"],
    "max_evidence_cases": 8
  }
  ```
- **Response:**
  ```json
  {
    "query": "Why do users fail when searching for family members?",
    "grounding_status": "FULLY_GROUNDED",
    "synthesis": "Users fail during family member retrieval primarily due to the Kinship Vocabulary Gap...",
    "cited_cases": [
      {
        "external_id": "interview-c02-s05",
        "source": "1:1 User Interview",
        "quote": "User queried '5 sisters' and received zero results...",
        "relationship": "SUPPORTS"
      }
    ],
    "contradictions": null
  }
  ```

#### 3. `GET /api/v1/evidence`
Queries and filters master evidence cases.
- **Query Parameters:** `source_type`, `methodology`, `failure_mode`, `category`, `limit`, `offset`.

#### 4. `GET /api/v1/evidence/{external_id}`
Retrieves a single evidence record with complete provenance, debrief notes, and child vector chunks.

#### 5. `POST /api/v1/experiment/regression`
Executes the locked 8-case photo benchmark (`part1_experimental_benchmark.json`) and verifies that retrieval metrics maintain exact parity with `part1_experiment_results.json`.
- **Response:**
  ```json
  {
    "timestamp": "2026-10-01T03:00:00Z",
    "benchmark_cases_evaluated": 8,
    "strategy_a_recall": 0.65,
    "strategy_b_recall": 1.00,
    "recall_improvement": 0.35,
    "parity_maintained": true
  }
  ```

#### 6. `GET /api/v1/health`
Returns system status: database connectivity, `pgvector` index status, local embedding model load state, and Gemini API readiness.

---

## 19. Frontend Requirements

### 19.1 Scope Boundary
> [!IMPORTANT]
> The frontend specified here is the **Part 1 Research Discovery & Evidence Console**.
> It is **NOT** the consumer-facing Memory Search product (Part 5).
> Its sole purpose is to allow evaluators, product managers, and engineers to interact with the Discovery Engine, inspect memory frames, verify candidate ranking, explore qualitative evidence, and audit grounded AI insights.

### 19.2 Required Screens & Capabilities
1. **Interactive Discovery Engine Playground:**
   - Text input for raw natural language queries (including Hinglish and colloquial phrases).
   - Real-time side-by-side display of:
     - Parsed V2 Memory Representation JSON.
     - Derived Retrieval Signals.
     - Candidate Pool table showing Rank, Score, Compositional Breakdown, and Active Retrieval Paths.
     - Coverage Status badge (`SUFFICIENT` vs. `RECOVERY TRIGGERED`).
2. **Grounded Research Insight Explorer:**
   - Research question input box with source methodology toggles (`Unsolicited Public`, `Prompted Interview`).
   - Markdown synthesis panel displaying the Gemini output.
   - Interactive citation tooltips: clicking `[CASE: interview-c02-s05]` opens a modal displaying the exact raw interview excerpt, participant debrief, and document provenance.
   - Contradiction Callout boxes highlighting divergent evidence.
3. **Master Evidence Repository Browser:**
   - Filterable data table of the ingested qualitative research evidence cases.
   - Filters for source, methodology, failure mode, and signal strength.
4. **Regression Test Dashboard:**
   - Single-button trigger to execute the 8-case benchmark suite.
   - Displays live metrics table comparing Strategy A (Direct Baseline) vs. Strategy B (Discovery Engine) against locked baseline numbers.

---

## 20. Security Architecture

1. **API Key Isolation:**
   - The `GEMINI_API_KEY` is injected exclusively into the Railway environment. It is never transmitted to Vercel or exposed in client bundles.
2. **Database Access Control:**
   - Supabase connection strings use PostgreSQL role-based authentication. The FastAPI backend connects via a dedicated `discovery_app` role with permissions restricted strictly to the application schema.
   - Row Level Security (RLS) is enabled on all tables, with read-only access granted to authenticated backend clients.
3. **CORS Restrictions:**
   - FastAPI CORS middleware explicitly whitelists only the production Vercel domain and `localhost:3000` for development. Wildcard origins (`"*"`) are strictly prohibited.
4. **Input Sanitization:**
   - All user query strings undergo strict Pydantic length validation (maximum 500 characters) and null-byte stripping to prevent SQL injection or vector query poisoning.

---

## 21. Concrete Deployment Architecture

```
┌────────────────────────────────┐         ┌────────────────────────────────┐
│         VERCEL (EDGE)          │  HTTPS  │        RAILWAY (PAAS)          │
│ • Next.js 14 App Router        │ ──────► │ • Python 3.11 + FastAPI        │
│ • Static Assets & SSR          │  REST   │ • Uvicorn ASGI Worker          │
│ • Client State (Zustand/Query) │         │ • Sentence-Transformers Local  │
└────────────────────────────────┘         └────────────────────────────────┘
                                                           │
                                                           │ Internal Network
                                                           ▼
                                           ┌────────────────────────────────┐
                                           │       SUPABASE (MANAGED)       │
                                           │ • PostgreSQL 15                │
                                           │ • pgvector (HNSW Cosine Index) │
                                           │ • Full-Text Search (tsvector)  │
                                           └────────────────────────────────┘
```

### 21.1 Environment Variable Specification

#### Vercel Environment Variables
```env
NEXT_PUBLIC_API_BASE_URL=https://discovery-engine-backend.up.railway.app
NEXT_PUBLIC_APP_ENV=production
```

#### Railway Environment Variables
```env
PYTHONUNBUFFERED=1
PORT=8000
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
GEMINI_API_KEY=AIzaSy...[REDACTED]
EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-small # Initial benchmark candidate; set to benchmark winner
USE_MINILM_FALLBACK=false
CORS_ORIGINS=https://discovery-engine.vercel.app,http://localhost:3000
```

---

## 22. Free-Tier Constraints & Mitigations

To guarantee 100% feasibility under Railway and Supabase free/starter operational limits:

| Platform | Free/Starter Tier Limit | Potential Risk | Architectural Mitigation Implemented |
| :--- | :--- | :--- | :--- |
| **Railway** | 512 MB – 1 GB RAM | OOM killed when loading heavy ML models | Evaluates lightweight 384-dim candidates (Initial Benchmark Candidate `intfloat/multilingual-e5-small` at ~470MB disk, ~600MB peak RAM vs. fallback `paraphrase-multilingual-MiniLM-L12-v2` at ~650MB peak RAM). Winning model is locked post-benchmark and loaded lazily as a singleton. Avoids PyTorch CUDA dependencies via CPU-only wheels. |
| **Railway** | Ephemeral Disk | Lost model weights on container restart | Hugging Face cache directory (`HF_HOME`) is bundled or pre-downloaded during Docker image build, eliminating runtime download latency and bandwidth quotas. |
| **Supabase** | 500 MB Database Space | Database storage cap exceeded | The curated qualitative evidence corpus with 384-dim vectors requires < 10 MB of total storage. Indexes fit comfortably within shared memory buffers. |
| **Supabase** | Connection Pooling Limit | Exceeding direct Postgres connections (max 60) | FastAPI utilizes an `asyncpg` connection pool with `max_size=10` and `min_size=2`, connecting through Supabase's transaction pooler (port 6543). |
| **Gemini API**| 15 RPM (Free Rate Limit) | 429 Too Many Requests | Backend implements an asynchronous token-bucket rate limiter and exponential backoff retry policy ($base=2s, max\_retries=3$). |

---

## 23. Deterministic vs. LLM Responsibilities

To ensure predictable system performance and prevent runaway latency, responsibilities are strictly partitioned:

| Pipeline Responsibility | Execution Mechanism | LLM Involvement | Rationale |
| :--- | :--- | :--- | :--- |
| **Input Sanitization** | Deterministic Python regex | None | Zero latency, deterministic security. |
| **Vernacular Particle Stripping** | Deterministic dictionary match | None | Known Hinglish particles (`ki`, `wali`) must be handled without LLM variance. |
| **V2 Schema Parsing (Canonical)** | Deterministic rule engine | None | Known benchmark cases must produce 100% identical frames every run. |
| **V2 Schema Parsing (Open-Domain)**| Few-shot Gemini parser | **LLM (Structured Output)** | Handles unexpected conversational phrasing when rules don't match. |
| **Retrieval Signal Derivation** | Deterministic mapping logic | None | Intermediate search primitives must be mathematically predictable. |
| **Candidate Discovery (Stage 4)** | PostgreSQL FTS & pgvector | None | Pure database operations. |
| **Coverage Checking (Stage 4)** | Deterministic threshold checks | None | Hard boundary conditions, zero ambiguity. |
| **Controlled Recovery (Stage 4)** | Deterministic broadening logic | None | Guaranteed finite execution without autonomous looping. |
| **Compositional Matching (Stage 5)**| Deterministic arithmetic formula | None | Entity-attribute binding scores must be completely auditable. |
| **Result Organization (Stage 6)** | Deterministic temporal clustering | None | Chronological preservation requires mathematical grouping. |
| **Research Synthesis (RAG)** | Grounded Gemini Generator | **LLM (Constrained RAG)** | Qualitative summarization requires natural language synthesis. |
| **Grounding & Quote Verification** | Deterministic GroundingValidator | None | Verifies exact case existence, verbatim quote substring matching, and claim-quote consistency. |

---

## 24. Failure Handling & Circuit Breakers

| Failure Scenario | Immediate System Reaction | User-Facing Fallback State |
| :--- | :--- | :--- |
| **Gemini API Outage / 503 / Rate Limit** | FastAPI catches HTTP error, attempts 3 exponential backoffs. | Returns raw retrieved evidence cases directly without synthesis, accompanied by warning: *"AI Synthesis temporarily unavailable. Raw evidence records displayed."* |
| **Local Embedding Model OOM** | Catch container memory alert on startup. | If enabled, automatically switches to lightweight `paraphrase-multilingual-MiniLM-L12-v2` or falls back entirely to PostgreSQL Lexical FTS search. |
| **Supabase Connection Loss** | Connection pool timeout after 5 seconds. | Returns HTTP 503 with structured error: `DATABASE_UNAVAILABLE`. |
| **Candidate Pool Empty After Recovery** | Controlled recovery executes secondary broadening pass. If still 0 candidates: | Returns empty result set with diagnostic flag: `ZERO_CANDIDATES_RECOVERED` and highlights which query dimension caused the drop. |
| **Ungrounded Gemini Claim** | GroundingValidator detects a claim failing verbatim quote verification or claim-quote consistency check. | Strips the ungrounded claim from the response and downgrades `grounding_status` to `QUALIFIED`. If $>50\%$ of claims fail, falls back to raw evidence records. |

---

## 25. Logging, Diagnostics, and Observability

Every execution through the Discovery Engine generates a structured JSON trace logged to stdout:

```json
{
  "trace_id": "tr-7f8a9b1c",
  "timestamp": "2026-10-01T03:15:22.104Z",
  "raw_input": "rohtang ki ice wali photo",
  "stages": {
    "stage_2_interpretation_ms": 1.2,
    "stage_3_signal_generation_ms": 0.4,
    "stage_4_retrieval_ms": 14.8,
    "stage_4_coverage_status": "COVERAGE_SUFFICIENT",
    "stage_4_recovery_triggered": false,
    "stage_5_compositional_matching_ms": 2.1,
    "stage_6_organization_ms": 0.8
  },
  "candidate_metrics": {
    "total_pool_size": 18,
    "rank_1_candidate_id": "c2_tgt_rohtang_snow_jacket",
    "rank_1_score": 2.5
  },
  "grounding_status": "N/A"
}
```

---

## 26. Testing Strategy

The test suite enforces end-to-end verification across 8 distinct test categories:

```mermaid
flowchart TD
    T1["Unit Tests<br/>(Pydantic V2 validation, rule parsers, RRF math)"]
    T2["Ingestion Tests<br/>(Manifest-driven validation, schema integrity, zero nulls)"]
    T3["Retrieval Tests<br/>(Vector similarity, FTS ranking, multi-path merge)"]
    T4["Grounding Tests<br/>(Assert every claim contains verified verbatim quote snippet)"]
    T5["Contradiction Tests<br/>(Verify conflicting evidence triggers dual-perspective output)"]
    T6["Source-Comparison Tests<br/>(Verify Play Store vs Reddit vs Interview distribution)"]
    T7["Regression Suite<br/>(8 benchmark cases maintain +35% recall gain against baseline)"]
    T8["Deployment Smoke Tests<br/>(Health check, latency < 2000ms, DB connection)"]

    T1 --> CI["Automated CI Pipeline (GitHub Actions / Railway PR Check)"]
    T2 --> CI
    T3 --> CI
    T4 --> CI
    T5 --> CI
    T6 --> CI
    T7 --> CI
    T8 --> CI
```

### 26.1 Benchmark Regression Test Definition
The test file `tests/test_benchmark_regression.py` executes the identical protocol from `run_part1_experiment.py`:
- Ingests `part1_experimental_benchmark.json` (65 candidates).
- Runs Strategy A (Literal Baseline) and Strategy B (Discovery Engine) across the 8 locked canonical queries using benchmark test fixture handlers (`tests/fixtures/benchmark_handlers.py`).
- Asserts:
  - Strategy B Mean Recall == 1.00.
  - Strategy B Mean P@1 $\ge$ 0.78.
  - Zero-Result Failure Cases == 0.
  - Case 7 Multi-Session Coverage == 10 of 10 days.

---

## 27. Evaluation Methodology

### 27.1 Evaluation Boundary
> [!IMPORTANT]
> The evaluation methodology specified here assesses whether the **deployed software system functions correctly as an evidence-discovery and multi-path retrieval engine**.
> 
> Consistent with Part 2 findings, **this evaluation does NOT claim to measure or prove real-world human retrieval success**. Evaluating human cognitive recognition and task completion belongs strictly to later user-facing validation phases.

### 27.2 System Evaluation Criteria
1. **Retrieval Parity:** Deployed FastAPI pipeline must match the offline Python prototype results with 100% precision.
2. **Grounding Accuracy:** 100% of substantive claims generated by the RAG endpoint must match an existing database record UUID and pass server-side verbatim quote snippet verification against raw source text.
3. **Execution Latency:**
   - Multi-path photo discovery query $\le$ 250ms (p95).
   - Grounded RAG synthesis query $\le$ 2,500ms (p95).
4. **Availability:** System maintains $\ge$ 99.5% uptime on free-tier infrastructure under test load.

---

## 28. Implementation Sequence

The implementation is structured into 6 sequential phases. No phase may begin until the preceding phase passes its validation gate:

```
┌────────────────────────────────────────────────────────┐
│  PHASE 1: Database Setup & Evidence Ingestion          │
│  • Supabase setup, pgvector activation, DDL migration  │
│  • Ingest & chunk curated research evidence cases      │
│    according to declarative manifest thresholds        │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  PHASE 2: Local Embedding & Hybrid Retrieval Core      │
│  • Execute Railway deployment embedding benchmark      │
│  • Select and lock the winning embedding model based   │
│    on the benchmark                                    │
│  • Set EMBEDDING_MODEL_NAME to the selected model      │
│  • Implement FTS, vector search, RRF candidate merging │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  PHASE 3: Discovery Engine Pipeline Implementation     │
│  • Stages 2–6 (V2 schema, signals, coverage, recovery, │
│    compositional matching, result organization)        │
│  • Pass 8-case benchmark regression test               │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  PHASE 4: Server-Side Grounded RAG & Quote Validator   │
│  • Implement structured JSON prompt with quotes        │
│  • Build server-side GroundingValidator                │
│  • Build contradiction detection & source comparison   │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  PHASE 5: FastAPI REST Endpoints & API Hardening       │
│  • Implement /discover, /research/insights, /evidence  │
│  • Add rate limiting, CORS, error handling, logging    │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  PHASE 6: Interactive Console Frontend & Deployment    │
│  • Next.js interactive console on Vercel               │
│  • Deploy backend to Railway, wire Supabase & Gemini   │
│  • Execute full end-to-end smoke test suite            │
└────────────────────────────────────────────────────────┘
```

---

## 29. Definition of Done

The implementation of Part 1 will be considered **DONE** when and only when all of the following conditions are satisfied:

- [ ] Full qualitative evidence corpus across Play Store (245 cases), Reddit (38 cases), and Interviews (25 retrieval episodes), totaling 308 master records (with optional 23/50 historical subsets preserved), is ingested into Supabase according to manifest thresholds with full provenance and vector chunks.
- [ ] Local embedding model loads and computes 384-dim vectors on Railway without crashing or exceeding RAM limits, verified via `scripts/benchmark_embeddings.py`.
- [ ] Stages 2 through 6 of the Discovery Engine pipeline execute end-to-end via `POST /api/v1/discover`.
- [ ] The automated regression test (`pytest tests/test_benchmark_regression.py`) passes with 100% parity against `part1_experiment_results.json`.
- [ ] The RAG endpoint (`POST /api/v1/research/insights`) produces syntheses where 100% of claims cite verified database case IDs and pass server-side verbatim quote snippet verification.
- [ ] Contradictions between public reviews and interviews are surfaced explicitly without forced narrative smoothing.
- [ ] FastAPI backend is live and healthy on Railway with HTTPS.
- [ ] Next.js Interactive Research Console is live on Vercel, securely communicating with Railway.
- [ ] No Part 1 conceptual artifacts were modified.
- [ ] No Part 5 Memory Search consumer UI was built.

---

## 30. Open Implementation Decisions

The following engineering choices were not determined by the conceptual Part 1 artifacts and are explicitly documented here:

1. **IMPLEMENTATION DECISION REQUIRED: Embedding Precision (Float32 vs. Half-Precision Float16)**
   - *Options:* Use standard 32-bit floating point vectors vs. 16-bit half-precision (`FP16`).
   - *Recommendation:* Use standard `Float32` initially, as the curated qualitative evidence chunks consume negligible storage (<10MB). If the corpus scales beyond 10,000 chunks, migrate to `FP16` to save 50% memory.
2. **IMPLEMENTATION DECISION REQUIRED: RRF Constant Value ($k$)**
   - *Options:* Standard $k=60$ vs. tuning $k$ between 20 and 100.
   - *Recommendation:* Fix $k=60$ as per standard Information Retrieval literature; empirical tuning is unnecessary at this benchmark scale.
3. **IMPLEMENTATION DECISION REQUIRED: Local Model Pre-Caching Strategy in Docker**
   - *Options:* Download weights at container runtime vs. baking weights into Docker image layers during CI build.
   - *Recommendation:* Bake weights into the Docker build to guarantee zero cold-start download delay on Railway.

---

## 31. Final Consistency Audit

Before finalizing this specification, an internal consistency audit was performed against all existing project artifacts:

| Audit Item | Verification Status | Exact Consistency Check & Rationale |
| :--- | :---: | :--- |
| **Locked Part 1 Artifacts Preserved?** | **PASS** | Zero modifications made to `part1_memory_representation_schema_v2.md`, `part1_discovery_engine_architecture_final.md`, `part1_discovery_engine_operating_spec_final.md`, or experiment result files. |
| **V2 Schema Exact Compliance?** | **PASS** | Pydantic v2 data models match the locked JSON schema exactly: `events` is an optional object (`event_name`, `sub_event`); `spatial_setting` is a string; `possessive` is used instead of `possession`; `temporal_nature` matches the exact 4 locked enum values (`COARSE_YEAR_ERA`, `RELATIVE_OFFSET`, `SEASON_EVENT_BOUND`, `EXACT_MONTH_YEAR`); all models enforce `extra="forbid"`. |
| **Corpus Counts & Dynamic Ingestion?** | **PASS** | Removed rigid "113" and uncontextualized "23/50" assumptions. The primary ingestion architecture is configured for the authoritative project corpus of 308 records (245 Play Store cases + 38 Reddit cases + 25 interview retrieval episodes), while explicitly preserving source/methodology distinctions and retaining earlier 23/50 Play Store batches only as optional curated subsets. |
| **Experimental Proxies vs. Permanent Rules?** | **PASS** | Permanent engine mechanisms (entity-attribute binding, Hinglish particle stripping, coarse temporal bounding, OCR routing) are strictly separated from benchmark-specific test fixtures (demographic proxying for kinship, COVID epoch boundary) in accordance with the locked architecture. |
| **Embedding Selection Reframed?** | **PASS** | Embedding model selection is reframed as an empirical deployment benchmark decision on Railway with `intfloat/multilingual-e5-small` designated as the Initial Benchmark Candidate and `paraphrase-multilingual-MiniLM-L12-v2` as fallback, evaluating container RAM under load, inference latency, and Hinglish retrieval quality. |
| **Grounding Validation Strengthened?** | **PASS** | Replaced simple citation-ID existence check with a multi-stage `GroundingValidator` enforcing verbatim quote substring matching, heuristic Claim-Quote Consistency Checks (token overlap), and automated ungrounded claim degradation. |
| **Subsystem A vs. Subsystem B Delineated?** | **PASS** | Crystal-clear separation established between Subsystem A (Algorithmic Discovery Engine Core for photo candidate retrieval) and Subsystem B (Qualitative Research Evidence RAG Console for research intelligence). |
| **Zero Paid Embedding APIs?** | **PASS** | 100% open-source local embedding model running on Railway CPU. |
| **No Premature Part 5 UI?** | **PASS** | Frontend is strictly defined as an internal Research Discovery Console for evidence analysis, not the consumer photo search product. |
| **Causal Boundary Preserved?** | **PASS** | Specification explicitly maintains that Part 1 evaluates candidate recovery in an evidence system, not end-to-end human retrieval success. |
