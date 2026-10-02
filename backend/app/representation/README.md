# Representation Pipeline Module (Step 4)

**Implementation Status: Complete (Step 4 — V2 Memory Representations)**
**Governed strictly by:**
- `part1_memory_representation_schema_v2.md`
- `part1_discovery_engine_implementation_spec.md` (Sections 7.1, 7.2, 8.2, 23, 24)
- `part1_discovery_engine_operating_spec_final.md` (Canonical Traces 1–8)
- `database/migrations/001_initial_schema.sql` (Table: `memory_representations`)

## Architecture & Components
1. **`models.py`**:
   - `PersonConcept`, `EventConcept`, `ObjectConcept`, `TemporalConcept`, `V2MemoryRepresentation`
   - Strict adherence to locked V2 schema with `ConfigDict(extra="forbid")`.
   - Rejects ungrounded field fabrication while strictly preserving verbatim `raw_input`.
2. **`rules.py`**:
   - Deterministic rule-based extraction engine for canonical and generalized search patterns.
   - Hinglish / vernacular particle identification and normalization without modifying `raw_input`.
   - Canonical case support for all 8 benchmark cases from the operating spec.
   - Ambiguity / open-domain classification for routing fallback requests.
3. **`gemini_parser.py`**:
   - Structured JSON fallback parser using Gemini 2.5 Flash for ambiguous open-domain queries.
   - Robust error handling: catches timeouts, HTTP errors, and malformed JSON.
   - Zero credentials exposed or logged; fully mockable interface for deterministic unit testing.
4. **`interpreter.py`**:
   - `MemoryInterpreter` orchestrator executing: Sanitization $\rightarrow$ Deterministic Parsing $\rightarrow$ Ambiguity Check $\rightarrow$ Gemini Fallback (if applicable) $\rightarrow$ Schema Validation.
5. **`persistence.py`**:
   - Idempotent persistence to Supabase `memory_representations` table.
   - Preserves referential integrity to `evidence_cases`.
   - Guarantees zero alterations to `evidence_cases`, `evidence_chunks`, or `sources`.
