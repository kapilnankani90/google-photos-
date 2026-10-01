# Database & Migrations Foundation

**Implementation Status: Deferred to Step 2 (Supabase Foundation)**  
**Engineering Contract:** `part1_discovery_engine_implementation_spec.md` (Section 4)

## Architecture & Implementation Boundary
- Direct database schema migration is scheduled strictly for **Step 2 — Supabase Foundation**.
- During **Step 1 (Repository & Local Foundation)**, no active SQL schema is executed, no database connections are established, and no database credentials are required.
- The approved 9-table schema (`sources`, `evidence_cases`, `evidence_chunks`, `memory_representations`, `retrieval_signals`, `research_queries`, `claim_citations`, `benchmark_candidates`, `experiment_runs`) remains locked in the engineering specification and will be applied as version-controlled migrations during Step 2.
