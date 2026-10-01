# Retrieval & Scoring Pipeline Module

**Scheduled for Implementation: Step 6 (Retrieval)**  
**Governed by:**
- `part1_discovery_engine_architecture_final.md` (Stages 3–6)
- `part1_discovery_engine_implementation_spec.md` (Sections 8, 10–13)

## Scope
- `SignalGenerator`: Generates multi-modal search probes (visual entities, bound attributes, action signals, temporal intervals, literal OCR tokens)
- `MultiPathRetriever`: Coordinates lexical (PostgreSQL FTS), semantic (`pgvector` cosine), metadata, and temporal query paths
- `ReciprocalRankFusion`: Deterministic candidate merging ($k=60$)
- `CoverageChecker`: Deterministic threshold evaluation (volume, dimensional representation, temporal span)
- `ControlledRecovery`: Single-pass broadening engine ($MaxRetries = 1$)
- `CompositionalScorer`: Entity-attribute binding bonus and distractor penalty scoring
- `ResultOrganizer`: Contextual temporal clustering and session boundary preservation
