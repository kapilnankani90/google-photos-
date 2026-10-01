# Part 1 — Discovery Engine Experimental Specification

## 1. Experimental Objective

The objective of this specification is to define the smallest testable Discovery Engine prototype capable of evaluating the core conceptual hypothesis of Part 1:

$$\mathbf{PROJECT\ ANCHOR:}\ \text{Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching.}$$

$$\mathbf{PRIMARY\ EXPERIMENTAL\ QUESTION:}\ \text{Can the proposed Discovery Engine transform imperfect, natural human memory descriptions into retrieval representations}$$
$$\text{that recover relevant photo candidates more effectively than literal/direct query interpretation?}$$

### Scope & Experimental Principle
- **What this experiment is:** A minimal, controlled experimental proof-of-concept designed to test whether the conceptual pipeline (Interpretation $\rightarrow$ Signal Generation $\rightarrow$ Multi-Path Discovery $\rightarrow$ Coverage Check $\rightarrow$ Compositional Matching) functions as hypothesized.
- **What this experiment is not:** It is **not** a production-scale Google Photos search engine, **not** the user-facing MVP, and **not** a user interface.
- **Evidence Anchor:** All test inputs, failure behaviors, and candidate scenarios are derived directly from the real evidence documented in [part1_combined_evidence.md](file:///d:/graduation%20project%203/part1_combined_evidence.md) and [interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md).
- **Non-Claim Boundary:** This experiment does not claim to prove broad production search engine performance or user satisfaction; it tests the representational and retrieval validity of the locked Part 1 architecture.

---

## 2. Experimental Input

The experimental inputs consist of natural-language memory expressions representing real user retrieval tasks documented in project research:

1. **Case 1: `"5 sisters"`** (Social role / kinship and cardinality; Ep 05)
2. **Case 2: `"rohtang ki ice wali photo"`** (Vernacular code-mixing and spatial landmark; Ep 06 & 07)
3. **Case 3: `"white bike"`** (Entity-attribute binding; Ep 13)
4. **Case 4: `"diya at the gate"`** (Multi-object co-occurrence with unindexed acquaintance; Ep 25)
5. **Case 5: `"Progressive"`** (Literal in-image text vs. conversational prompt; Reddit Case 5)
6. **Case 6: `"document around 4 years ago"`** (Approximate temporal offset and sparse memory; Ep 10)
7. **Case 7: `"yellow truck"`** (Multi-session event retrieval and coverage check; Reddit Case 11)
8. **Case 8: `"wedding"`** (Broad event milestone and contextual organization; Reddit Case 10 & Ep 02)

No synthetic or artificial query scenarios outside the research evidence base are introduced.

---

## 3. Memory Representation

The experimental engine ingests each input and maps it into the locked [V2 Memory Representation Schema](file:///d:/graduation%20project%203/part1_memory_representation_schema_v2.md) without adding extraneous fields. Verbatim `raw_input` is preserved in every case.

Below are the exact structured representations generated for each test case:

### Case 1: "5 sisters"
```json
{
  "raw_input": "5 sisters",
  "people": [
    {
      "role": "sister",
      "count": 5
    }
  ]
}
```

### Case 2: "rohtang ki ice wali photo"
```json
{
  "raw_input": "rohtang ki ice wali photo",
  "objects": [
    {
      "name": "ice"
    }
  ],
  "spatial_setting": "rohtang"
}
```

### Case 3: "white bike"
```json
{
  "raw_input": "white bike",
  "objects": [
    {
      "name": "bike",
      "attributes": [
        "white"
      ]
    }
  ]
}
```

### Case 4: "diya at the gate"
```json
{
  "raw_input": "diya at the gate",
  "objects": [
    {
      "name": "diya"
    }
  ],
  "spatial_setting": "gate"
}
```

### Case 5: "Progressive"
```json
{
  "raw_input": "Progressive",
  "literal_text": [
    "Progressive"
  ]
}
```

### Case 6: "document around 4 years ago"
```json
{
  "raw_input": "document around 4 years ago",
  "objects": [
    {
      "name": "document"
    }
  ],
  "temporal": {
    "raw_time_expression": "around 4 years ago",
    "coarse_value": "4 years ago",
    "temporal_nature": "RELATIVE_OFFSET"
  }
}
```

### Case 7: "yellow truck"
```json
{
  "raw_input": "yellow truck",
  "objects": [
    {
      "name": "truck",
      "attributes": [
        "yellow"
      ]
    }
  ]
}
```

### Case 8: "wedding"
```json
{
  "raw_input": "wedding",
  "events": {
    "event_name": "wedding"
  }
}
```

---

## 4. Retrieval Signal Generation

Retrieval Signal Generation derives searchable representations from interpreted meaning. In accordance with the locked architecture, this is conceptually separate from interpretation.

For this minimal experiment, the following retrieval signals are generated:

| Case | Interpreted Meaning | Experimental Retrieval Signals Generated | Signal Modality |
| :--- | :--- | :--- | :--- |
| **1. "5 sisters"** | `people: [role="sister", count=5]` | Demographic candidate cue: `group_count: 5`, demographic primitive: `female/woman/girl` *(experimental translation proxy)* | Relational-derived & visual demographic |
| **2. "rohtang ki ice wali"** | `spatial="rohtang"`, `objects=["ice"]` | Spatial signal: `location: "rohtang"`, Visual entity signal: `terrain: "snow/ice"` *(grammatical particles stripped)* | Spatial setting & visual entity |
| **3. "white bike"** | `objects: [name="bike", attr=["white"]]` | Bound signal: `[entity: "bike", attribute: "white"]`; fallback entity: `"bike"` | Bound entity-attribute & visual entity |
| **4. "diya at the gate"** | `objects=["diya"]`, `spatial="gate"` | Co-occurring signals: `entity: "diya/lamp"`, `spatial: "gate/entrance"` | Visual entity & spatial setting |
| **5. "Progressive"** | `literal_text: ["Progressive"]` | Literal text signal: exact token `"Progressive"` *(segregated from dialog)* | Literal in-image text |
| **6. "document around 4 years ago"** | `objects=["document"]`, `temporal=RELATIVE_OFFSET` | Visual signal: `type: "document"`; Temporal constraint: flexible continuous window `[t - 4.5y, t - 3.5y]` *(experimental offset calculation)* | Visual entity & temporal interval |
| **7. "yellow truck"** | `objects: [name="truck", attr=["yellow"]]` | Primary bound signal: `[entity: "truck", attribute: "yellow"]`; secondary entity: `"truck"` | Bound entity-attribute & visual entity |
| **8. "wedding"** | `events: {event_name="wedding"}` | Event milestone signal: `event: "wedding"` | Event milestone |

> [!NOTE]
> The demographic expansion (`sister` $\rightarrow$ `group of females`) and temporal window offset (`4 years ago` $\rightarrow$ `[t - 4.5y, t - 3.5y]`) are **experimental translation hypotheses** defined specifically to test retrieval recovery in this proof-of-concept. They are not permanent hardcoded architectural rules.

---

## 5. Candidate Discovery Experiment

The Candidate Discovery experiment evaluates whether the interpreted multi-path retrieval signals recover relevant candidate photos that baseline direct/literal interpretation misses.

### Experimental Comparison

For each test query, two retrieval strategies are executed against the test corpus:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CANDIDATE DISCOVERY EXPERIMENTAL COMPARISON                     │
├───────────────────────────────────────────┬────────────────────────────────────────────┤
│ STRATEGY A: DIRECT / LITERAL BASELINE      │ STRATEGY B: DISCOVERY ENGINE PIPELINE      │
├───────────────────────────────────────────┼────────────────────────────────────────────┤
│ • Treats query as literal keyword string. │ • Ingests query into V2 memory frame.      │
│ • Direct token lookup in metadata/tags.   │ • Generates multi-modal retrieval signals. │
│ • Fails on vernacular particles (wali).   │ • Activates multiple conceptual paths:     │
│ • Fails on social roles (sister).         │   - visual, attribute-bound, temporal,     │
│ • Fails when biometrics are unindexed.    │     spatial, relational, literal text.     │
│ • Evaluates single-query search pass.     │ • Aggregates into unified candidate pool.  │
└───────────────────────────────────────────┴────────────────────────────────────────────┘
```

### Purpose of Comparison
- To measure whether Strategy B admits the target candidate into the unified candidate pool where Strategy A drops it due to vocabulary mismatch, colloquial syntax, or single-path reliance.

---

## 6. Candidate Evaluation

Candidate photos admitted to the unified candidate pool are evaluated against the complete V2 memory frame.

### Experimental Evaluation Principles
The evaluation respects the core principles of the locked architecture:
1. **Entity-Attribute Binding:** Attributes are evaluated directly on their host entities. A candidate with a white motorcycle receives a higher score than a candidate with a black motorcycle next to a white background.
2. **Neutrality of Unspecified Dimensions:** If an attribute, location, or time expression is omitted in the query, it is treated as neutral (wildcard). It does not penalize the candidate photo.
3. **Temporal Approximation:** Candidates falling within the continuous temporal interval receive full or soft temporal congruence scores; exact day/month matches are not required.
4. **Soft Multi-Clue Satisfaction:** Candidates fulfilling primary clues but diverging slightly on a secondary detail are retained and scored proportionately rather than dropped.

### Experimental Scoring Proxy (Non-Production)
For prototype evaluation, a simple additive match score is calculated as an **experimental proxy**:

$$\text{Candidate Score} = \sum_{d \in \text{Populated Dimensions}} \text{Match}(d, \text{Candidate Photo})$$

Where $\text{Match}(d, \text{Photo}) \in [0.0, 1.0]$. 
- This formula is strictly an **experimental diagnostic tool** to rank candidates in the prototype. It is not part of the locked conceptual architecture.

---

## 7. Controlled Recovery Experiment

The experiment validates the architecture's ability to detect candidate under-retrieval and execute a controlled broadening step.

### Primary Test Case: "yellow truck"
- **Scenario:** The test corpus contains photos of a yellow utility truck photographed across multiple dates (simulating Reddit Case 11, where a user photographed a truck across 10 distinct days).
- **Initial Discovery Simulation:** The initial bound query probe captures photos from only 1 or 2 sessions.

### Experimental Coverage Check Rule
The prototype evaluates the following observable experimental condition:

$$\mathbf{Experimental\ Check:}\ \text{"Does the initial candidate set capture the recurring temporal span of the query entity?"}$$

- If candidates are clustered exclusively in an isolated session while broader temporal records exist for the entity, coverage is flagged as **INSUFFICIENT**.
- *Label:* This rule is an **experimental diagnostic rule** designed for testing recovery, not a fixed production threshold.

### Controlled Broadening Step
When coverage is flagged as insufficient:
1. **Relax Secondary Constraints:** Broadens the vehicle query to include related utility vehicle bodies.
2. **Query Complementary Paths:** Activates a temporal timeline scan around the identified trip dates.
3. **Merge Candidates:** Additional candidates discovered across the remaining dates are merged directly into the unified candidate pool without discarding earlier candidates.
4. **Re-evaluate:** The expanded pool is evaluated against the memory frame in Stage 5.

---

## 8. Test Data / Corpus Representation

### Inspection of Available Workspace Assets
A thorough inspection of workspace files was conducted prior to designing this specification:
- **Actual Photo Files:** None (`.jpg`, `.jpeg`, `.png`, `.webp`, `.heic` do not exist in the workspace).
- **Photo Metadata / EXIF Dumps:** None.
- **Screenshots:** None.
- **Available Data:** Qualitative interview behavioral episode transcripts (`interview_behavioral_episodes.md`), interview datasets (`interview_evidence_dataset.json`), Reddit review datasets (`reddit_evidence_dataset.json`), Play Store review datasets (`raw_reviews_dataset.json`), and consolidated research summaries (`part1_combined_evidence.md`).

### Controlled Candidate Corpus Representation
Because real photo media files do not exist in the repository, we explicitly define a **controlled benchmark candidate corpus representation**. This corpus represents photographs as structured JSON records containing visual, temporal, spatial, and textual properties.

This synthetic benchmark allows us to test the Discovery Engine's retrieval logic rigorously **without pretending it is a real Google Photos index**.

#### Candidate Record Schema:
```json
{
  "photo_id": "string",
  "visual_entities": ["string"],
  "bound_attributes": {
    "entity_name": ["attribute_value"]
  },
  "demographic_tags": {
    "count": "integer",
    "apparent_gender": "string",
    "apparent_age": "string"
  },
  "in_image_text": ["string"],
  "timestamp": "ISO-8601 string",
  "spatial_setting": "string",
  "event_context": "string",
  "is_ground_truth_target": "boolean",
  "target_case": "string"
}
```

The test corpus will include **ground truth target records** for all 8 test cases alongside **distractor/noise records** (e.g., photos with disconnected white objects, generic dog photos, unrelated documents, and separate wedding albums) to evaluate precision and ranking.

---

## 9. Experimental Output Structure

For every test query, the experimental engine must generate an inspectable JSON/text trace containing the following 10 diagnostic elements:

```
1. RAW MEMORY:            Verbatim input string
2. MEMORY REPRESENTATION: Populated V2 Memory Representation Frame
3. RETRIEVAL SIGNALS:     Derived multi-modal signals
4. DISCOVERY PATHS:       Active conceptual paths (visual, bound, spatial, temporal, literal)
5. INITIAL CANDIDATES:    Candidate records gathered in first pass
6. COVERAGE DECISION:     Sufficient vs. Insufficient (with diagnostic reason)
7. RECOVERY ACTION:       Broadening actions executed, if triggered
8. FINAL CANDIDATES:      Complete merged candidate set
9. CANDIDATE EVALUATION:  Compositional match assessment for each candidate
10. MATCH EXPLANATION:    Detailed reason why each candidate succeeded, ranked high, or was demoted
```

This output trace ensures that every stage of the pipeline can be independently audited.

---

## 10. Test Case Matrix

| Case | Memory Type | Main Architectural Hypothesis | Expected Failure in Direct Baseline | Expected Behavior in Discovery Engine | What We Measure |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. "5 sisters"** | Social role / kinship + count | Translating kinship into demographic primitives recovers unindexed family photos. | Returns 0 results because metadata has no "sister" tag. | Generates demographic probe (`5 females`); retrieves group portrait. | Target candidate admitted to pool; rank in top results. |
| **2. "rohtang ki ice wali photo"** | Vernacular syntax + spatial landmark | Raw input preservation and particle stripping prevents zero-result errors. | Fails completely on `wali photo` as search keywords. | Isolates `rohtang` and `ice`; retrieves mountain snow photos. | Zero-result avoidance; target retrieval in snowy mountain set. |
| **3. "white bike"** | Entity-attribute binding | Compositional evaluation prevents flooding from disconnected color matches. | Floods results with white shirts, walls, and dark vehicles. | Binds `white` to `bike`; elevates candidates with white vehicle bodies. | Precision at Top-K; ratio of true bound matches vs. background color noise. |
| **4. "diya at the gate"** | Co-occurring visual + spatial clues | Multi-path discovery recovers photos when biometric clustering is missing. | Fails because acquaintance (watchman) is unindexed in face albums. | Spatial + object paths co-discover gate and oil lamp candidates. | Candidate pool inclusion without biometric face tag dependency. |
| **5. "Progressive"** | Literal in-image text | Segregating literal text path isolates document search from dialog prompts. | Conversational model treats text as dialog prompt; returns refusal. | Routes literal text to in-image text matching; retrieves insurance bill. | Document retrieval success; elimination of conversational chatbot refusal. |
| **6. "document around 4 years ago"** | Coarse temporal offset + object | Continuous temporal windowing supports approximate human time memory. | Rejects non-ISO date string or demands exact calendar input. | Calculates open historical window; gathers documents from that era. | Candidate inclusion across multi-month window without exact day/month. |
| **7. "yellow truck"** | Multi-session entity + coverage gap | Candidate coverage checking detects single-session truncation and recovers full span. | Prematurely truncates results to 1–2 sessions, dropping 80% of photos. | Detects temporal clustering; broadens search to recover all 10 days. | Number of distinct event days recovered in candidate pool. |
| **8. "wedding"** | Broad milestone event | Contextual result organization keeps extended event photos accessible. | Returns isolated photos; scatters multi-day trip across time. | Retains event clustering and chronological landmarks. | Preservation of surrounding multi-day event coherence. |

---

## 11. Experimental Success Criteria

The experimental engine will be evaluated against the following observable success criteria:

1. **Meaning Preservation:** The Memory Interpretation Layer successfully converts natural expressions into valid V2 schemas without corrupting `raw_input` or dropping core entities.
2. **Vocabulary Bridge:** For relational queries (`"5 sisters"`), the engine admits candidates with matching visual demographics into the candidate pool where direct keyword lookup yields zero results.
3. **Vernacular Resilience:** Colloquial particles (`"wali photo"`) are successfully isolated, preventing zero-result failures.
4. **Attribute Binding Integrity:** In compositional queries (`"white bike"`), candidate photos containing the attribute bound directly to the target entity rank higher than candidates containing disconnected attribute matches.
5. **Multi-Path Retrieval:** Queries with missing face tags (`"diya at the gate"`) successfully surface candidates via spatial and object paths.
6. **Literal Text Isolation:** In-image text queries (`"Progressive"`) are processed as literal text searches rather than conversational conversational prompts.
7. **Coverage Recovery:** In the `"yellow truck"` test, the coverage check successfully detects single-session truncation and gathers candidates across the remaining days into the unified pool.
8. **Neutrality of Missing Clues:** In sparse queries (`"wedding"`, `"document around 4 years ago"`), missing location or person tags do not penalize matching photos.

---

## 12. Experimental Limitations

To maintain scientific integrity, the explicit limitations of this experiment are documented:

- **Not Real Google Photos Infrastructure:** This experiment runs against a controlled benchmark corpus; it does not access proprietary Google Photos production indexes or cloud storage.
- **Does Not Measure Real-World Latency:** Processing speeds in this small-scale test do not reflect production latency across 50,000+ photo collections.
- **Does Not Evaluate User Interface:** No UI layouts, touch gestures, or thumbnail grids are tested here; user presentation evaluation belongs to Part 5.
- **Does Not Prove End-User Satisfaction:** Retrieval success on benchmark records indicates architectural validity, not final subjective user satisfaction.
- **Architectural Proof-of-Concept:** This experiment is strictly designed to validate that the locked conceptual architecture functions logically before software implementation begins.

---

## 13. Next Action

Following the approval of this experimental specification, the immediate next step is:

$$\mathbf{NEXT\ STEP:}\ \text{Build the minimal Python experimental prototype script (e.g., \texttt{run\_part1\_experiment.py})}$$
$$\text{to execute the 8 test cases against the controlled benchmark corpus and output the inspectable diagnostic traces.}$$

- **Boundaries Maintained:**
  - Do **not** build the user-facing MVP.
  - Do **not** move to Part 5.
  - Do **not** select production databases or third-party cloud API services.
  - Focus strictly on running the small-scale architectural verification experiment for Part 1.
