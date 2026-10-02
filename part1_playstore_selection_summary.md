# Google Photos Part 1 — Phase 3B Play Store Evidence Selection Summary

**Authoritative Specification:** [`part1_discovery_engine_implementation_spec.md`](file:///d:/graduation%20project%203/part1_discovery_engine_implementation_spec.md)  
**Declarative Manifest:** [`config/ingestion_manifest.json`](file:///d:/graduation%20project%203/config/ingestion_manifest.json)  
**Raw Source Corpus:** [`raw_reviews_dataset.json`](file:///d:/graduation%20project%203/raw_reviews_dataset.json)  
**Output Dataset:** [`part1_playstore_evidence_245.json`](file:///d:/graduation%20project%203/part1_playstore_evidence_245.json)  
**Case Audit Log:** [`part1_playstore_selection_audit.md`](file:///d:/graduation%20project%203/part1_playstore_selection_audit.md)  
**Execution Date:** 2026-10-02

---

## 1. Executive Summary & Objective

In Phase 3B, we constructed and audited the authoritative Play Store retrieval evidence corpus from the pool of 1,456 raw scraped consumer reviews in `raw_reviews_dataset.json`. 

The primary objective was to extract authentic, reproducible, and methodologically defensible qualitative retrieval evidence representing real-world user memory retrieval behavior—specifically where users attempt to locate photos, videos, people, documents, or memories using remembered clues, face clustering, dates, or search queries.

In strict adherence to engineering constraints:
* **Zero Artificial Padding:** No reviews were fabricated or forced into the dataset merely to reach the 245 specification target.
* **Zero Duplication:** Every record maps to a unique, non-colliding `external_id` (190 distinct reviews).
* **Text Integrity:** All user review text is preserved verbatim without rewriting or synthetic expansion.
* **Pristine Preservation:** 100% of the 23 historical curated pristine Play Store cases are traceable and preserved.

---

## 2. Multi-Stage Selection Funnel

```
┌────────────────────────────────────────────────────────┐
│  RAW PLAY STORE SCRAPED CORPUS                         │
│  1,456 Raw Consumer Reviews                            │
└────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         ▼                                   ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│ STAGE 1: LEXICAL HEURISTIC  │   │ NON-LEXICAL POOL            │
│ 171 Keyword Candidates      │   │ 1,285 Raw Reviews           │
└─────────────────────────────┘   └─────────────────────────────┘
         │                                   │
         │ (Rubric filter:                   │ (Stage 2 Semantic
         │  126 passed, 22 pristine,         │  Expansion & Rubric Audit)
         │  23 excluded false positives)     │
         ▼                                   ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│ 126 Lexical Candidates      │   │ 41 Semantic Candidates      │
│ + 22 Pristine Cases         │   │ (Date, Face, Album Finding) │
└─────────────────────────────┘   └─────────────────────────────┘
         │                                   │
         └─────────────────┬─────────────────┘
                           │ + 1 Iconic Pristine Web Case (rev-user-c)
                           ▼
┌────────────────────────────────────────────────────────┐
│  FINAL DEFENSIBLE PLAY STORE CORPUS                    │
│  190 Structured Retrieval Evidence Cases               │
└────────────────────────────────────────────────────────┘
```

### Funnel Metrics Breakdown
1. **Total Scraped Raw Reviews:** 1,456 (100.0%)
2. **Low-Quality / Too Short (< 4 words / spam):** 363 (24.9%)
3. **Pure Non-Retrieval Exclusions (Billing/Storage rants, Video Editor, Crashes):** 37 (2.5%)
4. **General Gallery / Unrelated Photo Complaints (Sync deletes, UI rants):** 866 (59.5%)
5. **Total Audited Candidates:** 190 (13.1%)
   - **Historical Pristine Benchmarks:** 23 cases (12.1% of corpus)
   - **Stage 1 Lexical Candidates (Passed Rubric):** 126 cases (66.3% of corpus)
   - **Stage 2 Semantic Expansion (Discovered Beyond Lexical):** 41 cases (21.6% of corpus)

---

## 3. Target Count Diagnostic: 190 Defensible vs. 245 Target

* **Target Specification Count:** 245 Play Store cases
* **Actual Defensible Evidence Count:** 190 cases
* **Corpus Gap:** 55 cases (22.4% deficit against theoretical specification target)

### Why 245 Cannot Be Satisfied from Current Raw Evidence Without Compromise
An exhaustive semantic audit of all 1,456 reviews in `raw_reviews_dataset.json` reveals that exactly 190 reviews represent genuine, defensible photo retrieval situations. 

To force the count to 245 would require:
1. Including 55 reviews that are purely about Google One storage fees, subscription complaints, or cloud payment walls.
2. Including video editor and magic eraser UI complaints that contain zero search or retrieval behavior.
3. Including device deletion rants where users complain that deleting a photo from phone storage wiped it from cloud backup, without any attempt to search or retrieve.
4. Including 1-to-3 word spam reviews ("good app", "bad update").

**Conclusion:** Arbitrarily padding 55 non-retrieval reviews would directly violate the core engineering principle: *"Do not optimize for hitting 245. Optimize for producing a defensible, reproducible retrieval evidence corpus."* The 190 cases represent the complete empirical reality of the collected Play Store dataset.

---

## 4. Quantitative Corpus Distributions

### A. Star Rating Distribution (Balanced Positive & Negative Evidence)
| Star Rating | Case Count | Percentage | Research Function |
| :--- | :--- | :--- | :--- |
| **⭐ 1 Star** | 38 | 20.0% | Catastrophic failure modes, AI search regression, missing media |
| **⭐ 2 Stars** | 56 | 29.5% | Severe retrieval friction, forced manual scrolling, wrong faces |
| **⭐ 3 Stars** | 36 | 18.9% | Mixed retrieval experience, partial recognition, formatting limits |
| **⭐ 4 Stars** | 25 | 13.2% | Successful retrieval with feature improvement requests |
| **⭐ 5 Stars** | 35 | 18.4% | Benchmark retrieval success (demonstrating what clues succeed) |
| **Total** | **190** | **100.0%** | **Balanced across failure and success modes** |

### B. Evidence Type Distribution (Compatible with Supabase Schema)
| Evidence Type | Count | Share | Description |
| :--- | :--- | :--- | :--- |
| `FAILURE` | 94 | 49.5% | Search query failed, photo not found, wrong person clustered |
| `SUCCESS` | 56 | 29.5% | User successfully retrieves photos via face, date, or query |
| `NEUTRAL` | 40 | 21.1% | Feature request with retrieval context or mixed feedback |

### C. Primary Failure Mode Breakdown
| Failure Mode | Count | Share |
| :--- | :--- | :--- |
| `PERSON_NOT_RECOGNIZED` | 55 | 28.9% |
| `REQUIRES_EXACT_DATE` | 36 | 18.9% |
| `CONTEXT_NOT_UNDERSTOOD` | 31 | 16.3% |
| `NONE` (Success cases) | 19 | 10.0% |
| `INCOMPLETE_RESULTS` | 15 | 7.9% |
| `MANUAL_SCROLLING_REQUIRED`| 12 | 6.3% |
| `CANNOT_FIND_PHOTO` | 12 | 6.3% |
| `WRONG_PERSON` | 4 | 2.1% |
| `IRRELEVANT_RESULTS` | 3 | 1.6% |
| `OTHER` | 3 | 1.6% |

### D. What Users Remember (Retrieval Clues Used)
| Retrieval Clue Type | Count | Share |
| :--- | :--- | :--- |
| `PERSON_FACE` (Family, self, children) | 60 | 31.6% |
| `TEMPORAL_DATE` (Year, month, timeline era) | 46 | 24.2% |
| `NATURAL_LANGUAGE_DESCRIPTION` (Conversational prompt) | 40 | 21.1% |
| `SEARCH_KEYWORD` (Direct object or activity tag) | 22 | 11.6% |
| `ALBUM_CONTAINER` (Thematic album or event folder) | 11 | 5.8% |
| `OCR_DOCUMENT_TEXT` (Text in document or receipt) | 10 | 5.3% |
| `OBJECT_NAME` (Specific physical entity, e.g. cooling fan) | 1 | 0.5% |

---

## 5. Provenance & Integrity Validation

1. **Unique Identifiers:** All 190 records possess distinct, non-overlapping `external_id` values.
2. **Text Verbatim:** Review bodies are 100% untouched raw user text.
3. **Pristine Traceability:** 23 out of 23 historical pristine cases from `evidence_dataset.json` are retained with `historical_pristine = true`.
4. **Stream Purity:** 0 Reddit or Interview records are present in the Play Store corpus.
5. **Database Enum Conformance:** All `evidence_type` values strictly conform to `('FAILURE', 'SUCCESS', 'NEUTRAL')` as defined in `001_initial_schema.sql`.

---

## 6. Recommendations for Phase 3C

1. **Adopt 190 as the Defensible Play Store Baseline:**
   Update `config/ingestion_manifest.json` from `target_record_count: 245` to `target_record_count: 190` (Total project corpus: $190 + 38 + 25 = 253$ master evidence cases).
2. **Alternative (if 245 is an inflexible contractual mandate):**
   Execute a supplemental scrape of ~500 additional Play Store reviews via `google_play_scraper` specifically targeted at search and face queries to harvest the remaining 55 genuine retrieval cases, rather than padding non-retrieval complaints from the existing file.
