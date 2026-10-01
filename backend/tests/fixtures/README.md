# Test Fixtures & Benchmark Handlers

**Governed by:**
- `part1_discovery_engine_implementation_spec.md` (Section 8.3)

## Strict Architectural Isolation
As established in the locked architecture, the Discovery Engine does **not** hardcode domain assumptions (such as permanently equating "sister" with demographic tags or "before covid" with rigid date boundaries) into general production logic.

Specific mappings utilized during the controlled experiment are maintained in `benchmark_handlers.py` strictly as test fixtures for reproducing benchmark metrics, isolated from open-domain production pipelines.
