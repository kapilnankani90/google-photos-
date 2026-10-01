# Local Embedding Service Module

**Scheduled for Implementation: Step 5 (Embedding Benchmark & Model Selection)**  
**Governed by:**
- `part1_discovery_engine_implementation_spec.md` (Section 9)

## Scope
- Executes local 384-dimensional text embeddings on Railway CPU without paid external embedding APIs
- Model selection is determined strictly following execution of `scripts/benchmark_embeddings.py` on target container environment
- Evaluates candidate models (Candidate A: `intfloat/multilingual-e5-small`, Candidate B: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)
- Singleton embedder class with lazy model weight loading and thread-safe batch inference implemented post-benchmark
