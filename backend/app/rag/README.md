# Grounded Research RAG & Quote Validator Module

**Scheduled for Implementation: Step 7 (Grounded RAG)**  
**Governed by:**
- `part1_discovery_engine_implementation_spec.md` (Sections 14, 15, 16)

## Scope
- Server-side Gemini 2.5 Flash client constrained strictly to retrieved database evidence cases
- Zero-hallucination prompt formatting with mandatory `claim_text`, `cited_case_id`, and `verbatim_quote`
- Deterministic 3-Gate `GroundingValidator`:
  - Gate 1: Context membership check
  - Gate 2: Verbatim quote substring / fuzzy matching against raw text
  - Gate 3: Claim-quote consistency check (token overlap >= 40%)
- Structured contradiction detection across unsolicited public feedback vs. prompted interview protocols
