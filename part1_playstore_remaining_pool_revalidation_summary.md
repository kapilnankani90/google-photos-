# Phase 3B.3.2 — Remaining Supplemental Pool Re-Validation Summary

**Checkpoint:** Phase 3B.3.2 Audit Complete  
**Audit Execution Date:** 2026-10-02  
**Locked Project Requirement:** 245 Play Store Evidence Cases  

---

## Required 14-Point Reporting Breakdown

### 1. Number of Remaining Candidates Identified
**35** candidates were identified from the original 129-case valid supplemental pool that were not included in the first 94-case batch.

### 2. Number Audited
**35** candidates (100% of the remaining pool) were independently audited.

### 3. DIRECT_RETRIEVAL_EPISODE Count
**1** case (`REM-PLAY-011`): Concrete user retrieval episode where facial recognition conflates two cats (May vs Mari), causing incomplete search results when looking up photos of a specific pet/person.

### 4. VALID_RETRIEVAL_RELATED Count
**16** cases: Direct, substantive capability evidence on search indexing, face grouping, coordinates, AI search, and temporal date filters.

### 5. BORDERLINE Count
**12** cases: Ambiguous reviews mentioning search in passing, requesting nested album folders, or describing general gallery clutter without concrete retrieval mechanisms.

### 6. INVALID_NON_RETRIEVAL Count
**6** cases: 1 duplicate repost (`REM-PLAY-002`) + 5 non-retrieval reviews (Google Web search complaints, photo editor crop tools, cosmetic UI complaints, and generic praise).

### 7. Newly Defensible Cases
**17** cases ($1 \text{ episode} + 16 \text{ capability-related}$) meet the strict retrieval validity standard without any inferred details.

### 8. Duplicate Count
**1 duplicate identified** (`REM-PLAY-002`): Material duplicate repost of `SUPP-PLAY-085` (external ID `843344a6-0d23-4c6d-9ab4-e75a185d102b`) with identical review content and minor punctuation variations.

### 9. Inference-Error Count
**18 cases** in the remaining pool previously had retrieval attributes inferred from broad review phrases (e.g. inferring multi-clue retrieval from passing praise, or inferring photo retrieval from album picker requests). All inferred fields have been removed.

### 10. Combined Defensible Play Store Corpus
$$\text{Phase 3B.1 (151)} + \text{Phase 3B.3.1 (56)} + \text{Phase 3B.3.2 (17)} = \mathbf{224\text{ defensible cases}}$$

### 11. Remaining Gap to 245
$$\mathbf{245 - 224 = 21\text{ cases}}$$
The empirical gap to the locked requirement is narrowed from 38 down to **21 cases**.

### 12. Evidence Categories Represented by Newly Defensible Cases
- **Person / Relationship Retrieval (7 cases)**: Pet facial recognition conflation causing incomplete search results (`REM-PLAY-011`), failure to manually tag undetected faces (`REM-PLAY-004`), face grouping frequency inversion and mask failures (`REM-PLAY-006`), non-frontal angle tagging (`REM-PLAY-010`), pet historical retagging (`REM-PLAY-013`), 'Me' profile clustering failure (`REM-PLAY-014`), named search filtering (`REM-PLAY-017`).
- **General Retrieval Mechanics (6 cases)**: Filename indexing failure (`REM-PLAY-001`), scoped album search gap (`REM-PLAY-012`), numerical filename search friction across 2007+ archives (`REM-PLAY-015`), search regression returning 'no results' (`REM-PLAY-033`), search inaccuracy forcing visual inspection (`REM-PLAY-034`), search bar UI removal (`REM-PLAY-035`).
- **Temporal / Event Retrieval (2 cases)**: Absence of search by photo date (`REM-PLAY-003`), date range narrowing during search (`REM-PLAY-026`).
- **Location / Spatial Retrieval (1 case)**: Lat/long coordinate removal forcing Maps workaround (`REM-PLAY-005`).
- **Natural-Language / AI Search (1 case)**: AI search breaking basic keyword search on flagship hardware (`REM-PLAY-028`).

### 13. Evidence Categories Still Underrepresented
- **OCR / Text Inside Images**: While general keyword search is well-documented, specific optical character recognition failure cases remain relatively scarce.
- **Colloquial / Multilingual Retrieval**: Natural-language code-mixed queries (e.g. Hinglish / transliterated search) remain underrepresented in Play Store text compared to interview evidence.
- **Location / Geographic Map Search**: Only 1 new spatial retrieval case was defensibly established from this pool.

### 14. Whether Another Acquisition Step Appears Necessary
**YES.** Exactly **21 genuine retrieval cases** are required to reach the locked 245 target. Because the original 129 valid pool is now 100% audited ($94 + 35 = 129$), closing the final 21-case gap requires a targeted, precision scrape focusing on underrepresented categories (OCR document search, location map search, conversational AI photo search).

---

## Master Evidence Corpus Reconciliation

| Corpus Component | Locked Requirement | Phase 3B.1 | Phase 3B.3.1 | Phase 3B.3.2 | Combined Defensible | Remaining Gap |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Play Store Reviews** | **245** | 151 | +56 | **+17** | **224** | **21 cases** |
| **Reddit Cases** | **38** | 38 | 0 | 0 | **38** | **0 cases** |
| **Interview Episodes** | **25** | 25 | 0 | 0 | **25** | **0 cases** |
| **Total Master Evidence** | **308** | 214 | +56 | **+17** | **287** | **21 cases** |
