# Part 1 — Discovery Engine Operating Specification

## 1. Document Objective & Scope

The purpose of this document is to translate the **LOCKED** conceptual architecture defined in [part1_discovery_engine_architecture_final.md](file:///d:/graduation%20project%203/part1_discovery_engine_architecture_final.md) and the schema defined in [part1_memory_representation_schema_v2.md](file:///d:/graduation%20project%203/part1_memory_representation_schema_v2.md) into concrete, end-to-end operational traces using representative, real-world evidence cases.

$$\mathbf{PROJECT\ ANCHOR:}\ \text{Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching.}$$

This specification demonstrates how the seven-stage conceptual pipeline is designed to behave when presented with human memory expressions that are imperfect, colloquial, relational, sparse, or approximate.

> [!IMPORTANT]
> **Conceptual Specification Boundaries:**
> - This document is **not** an implementation or software specification.
> - It does **not** choose machine learning models, LLMs, vision backends, vector indexes, databases, or API protocols.
> - It does **not** design user interfaces, layouts, or wireframes.
> - It does **not** present empirical results; all traces describe expected conceptual behaviors and hypotheses to be tested during prototyping and Part 6 user evaluations.

---

## 2. End-to-End Conceptual Retrieval Traces

The eight traces below represent key failure modes and behavioral phenomena documented across 25 interview tasks ([interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md)) and 61 public review/community cases ([part1_combined_evidence.md](file:///d:/graduation%20project%203/part1_combined_evidence.md)).

---

### Case Trace 1: "5 sisters"

#### A. User Memory
The user remembers a group photograph of five young women who are siblings: `"5 sisters"`.

#### B. Memory Interpretation
- **`raw_input`:** `"5 sisters"`
- **Populated V2 Frame:**
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
- **Interpretation Scope:** Interpretation answers *"What does the user mean?"* It identifies a relational kinship role (`sister`) and an explicit cardinality (`count: 5`). It does not alter `raw_input` or force premature demographic conversion.

#### C. Retrieval Signals
- **Conceptual Responsibility:** Derives searchable representations from interpreted meaning.
- **Generated Signals:**
  - *Relational-Derived Demographic Signals:* Hypothesis of searchable demographic primitives corresponding to social role and group count (e.g., candidate concepts for groups of 5 women/girls).
  - *Cardinality Constraint:* Group count of 5 individuals.
- **Distinction from Interpretation:** Interpretation preserves the social relationship (`sister`); Signal Generation creates candidate visual search probes because personal photo libraries rarely index private family genealogical trees.

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Relational-Derived Path:* Active (queries media containing demographic clusters matching the group size and visual primitives).
  - *Visual Entity Path:* Active (queries multi-person group portraits).
- Unactivated paths (Temporal, Spatial, Action, Literal Text) remain neutral.

#### E. Unified Candidate Pool
- Candidate pool receives photographs containing groups of people, particularly groups of approximately five female individuals or multi-person family portraits.

#### F. Candidate Coverage Check
- **Evaluation:** The engine checks whether the candidate pool contains multi-person group photographs matching the cardinality constraint.
- **Outcome:** Sufficient. The collection yields plausible candidate groups; the engine proceeds directly to Multi-Clue Matching.

#### G. Controlled Recovery
- Not triggered (initial candidate coverage is sufficient).

#### H. Multi-Clue Matching
- Evaluates candidate photos against the populated frame:
  - Strongly scores photos matching both group cardinality (`count: 5`) and demographic congruence.
  - Absence of temporal, spatial, or action tags is treated as neutral (wildcard).

#### I. Result Organization
- Preserves contextual coherence by keeping candidate group portraits connected to their surrounding event timeline (e.g., family gatherings or holiday moments) rather than dispersing them across disconnected rows.

#### J. Recognition Endpoint
- The target photo of the five sisters is surfaced in initial visible results alongside surrounding family photos, allowing the user to immediately visually recognize the gathering.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 2 $\rightarrow$ Stage 3 (Interpretation to Retrieval Signal Generation).*
- **Why it breaks in baseline systems:** Commercial keyword and semantic systems often search literally for the label `"sister"` in metadata or vision tags. Because computer vision taggers output demographic tags (`"girl"`, `"woman"`) rather than kinship roles, direct search returns zero results (*"No results found"*).

#### L. Evidence Traceability
- **Source:** [interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md) — **Episode 05** (Candidate 2, Task 5: `5 sisters` returned 0 results; manual conversion to `5 girls` produced the target at Rank 1).

---

### Case Trace 2: "rohtang ki ice wali photo"

#### A. User Memory
The user recalls a photo taken in the snow at Rohtang Pass, expressed in conversational Hinglish: `"rohtang ki ice wali photo"`.

#### B. Memory Interpretation
- **`raw_input`:** `"rohtang ki ice wali photo"`
- **Populated V2 Frame:**
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
- **Interpretation Scope:** Identifies grammatical vernacular particles (`ki`, `wali`, `photo`) as communicative syntax, isolating the core geographic entity (`rohtang`) and physical element (`ice`).

#### C. Retrieval Signals
- **Generated Signals:**
  - *Spatial Setting Signal:* Geographic landmark / region concept (`Rohtang`, mountainous snow terrain).
  - *Visual Entity Signal:* Physical visual element (`ice`, `snow`).
- **Distinction:** Vernacular noise is stripped from the searchable signals while preserved in `raw_input`.

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Spatial / Environmental Path:* Searches geographic metadata and landscape scene tags for Rohtang or high-altitude terrain.
  - *Visual Entity Path:* Searches for visual snow/ice textures and winter outdoor settings.

#### E. Unified Candidate Pool
- Receives outdoor photos taken at high-altitude mountain passes, snowy landscapes, and geotagged or visually tagged Rohtang media.

#### F. Candidate Coverage Check
- **Evaluation:** Evaluates whether candidates represent the snowy mountain setting.
- **Outcome:** Sufficient. Candidates matching snowy mountain landscapes enter the pool.

#### G. Controlled Recovery
- Not triggered.

#### H. Multi-Clue Matching
- Evaluates candidates compositionally against both `spatial_setting: "rohtang"` and `objects: ["ice"]`.
- Elevates photos that satisfy both the location context and the salient visual snow element.

#### I. Result Organization
- Retains chronological and trip coherence, keeping photos from the mountain excursion grouped together so the user can identify the specific roadside or scenic stop.

#### J. Recognition Endpoint
- The user visually recognizes the snowy mountain backdrop and their attire from that specific vacation trip.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 2 (Memory Interpretation — Vernacular Syntax Rejection).*
- **Why it breaks in baseline systems:** Baseline search bars treat the colloquial Hindi postpositions `wali` and `photo` as literal query keywords, causing a complete lookup failure and returning an empty result screen.

#### L. Evidence Traceability
- **Source:** [interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md) — **Episode 06** (Candidate 2, Task 6: `rohtang ki ice wali photo` failed on `wali photo`; stripping to `rohtang ice pic` succeeded) and **Episode 07** (`marble cake wali photo`).

---

### Case Trace 3: "white bike"

#### A. User Memory
The user remembers a family member on a distinctive motorcycle: `"white bike"`.

#### B. Memory Interpretation
- **`raw_input`:** `"white bike"`
- **Populated V2 Frame:**
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
- **Interpretation Scope:** Binds the attribute modifier `white` directly to the host entity `bike`.

#### C. Retrieval Signals
- **Generated Signals:**
  - *Bound Entity-Attribute Signal:* `[Entity: bike | Attribute: white]`.
  - *Fallback Entity Signal:* `bike` (unbound, for candidate breadth).

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Bound Entity-Attribute Path:* Gathers photos containing white motorcycles or bicycles.
  - *Visual Entity Path:* Gathers general two-wheeled vehicles to protect against partial attribute tagging failures.

#### E. Unified Candidate Pool
- Unified candidate pool contains photographs featuring motorcycles and bicycles, with priority given to those exhibiting white or light-colored vehicle bodies.

#### F. Candidate Coverage Check
- **Evaluation:** Checks if two-wheeled vehicle candidates were successfully gathered.
- **Outcome:** Sufficient.

#### G. Controlled Recovery
- Not triggered.

#### H. Multi-Clue Matching
- **Compositional Responsibility:** Specifically evaluates `white` as a property of the `bike`.
- Prevents false-positive flooding: a candidate photo containing a black motorcycle next to a person in a white shirt is down-ranked relative to a candidate where the white color is localized directly on the vehicle.

#### I. Result Organization
- Retains surrounding context from the day the motorcycle ride occurred.

#### J. Recognition Endpoint
- The specific photograph of the family member posed on the white motorcycle is surfaced within the top visible results.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 5 (Multi-Clue Matching — Disconnected Attribute Scoring).*
- **Why it breaks in baseline systems:** Systems that evaluate queries as bag-of-words score `white` and `bike` independently, flooding top ranks with hundreds of photos containing white shirts, white walls, and unrelated dark vehicles.

#### L. Evidence Traceability
- **Source:** [interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md) — **Episode 13** (Candidate 3, Task 13: `white bike` retrieved the target at Position 1–3 because color was bound directly to the vehicle).

---

### Case Trace 4: "diya at the gate"

#### A. User Memory
The user remembers an evening photo of a residential watchman lighting a festival oil lamp at the entrance: `"diya at the gate"`.

#### B. Memory Interpretation
- **`raw_input`:** `"diya at the gate"`
- **Populated V2 Frame:**
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
- **Interpretation Scope:** Extracts the salient festival object (`diya`) and spatial architectural boundary (`gate`). Note that the person (`watchman`) was not explicitly named in the query text, demonstrating memory sparsity.

#### C. Retrieval Signals
- **Generated Signals:**
  - *Visual Entity Signal:* `diya` (oil lamp, small flame).
  - *Spatial Setting Signal:* `gate` (entrance gate, doorway, threshold).
  - *Co-occurrence Context:* Evening lighting / festival environment.

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Visual Entity Path:* Gathers photos with flame/diya tags or visual features.
  - *Spatial / Environmental Path:* Gathers photos taken near entry gates and doorways.
- Multi-path gathering ensures candidate retrieval even though face clustering is completely unindexed for this infrequent contact.

#### E. Unified Candidate Pool
- Contains photos of outdoor festival lighting, lamps near doorways, and entrance gate scenes.

#### F. Candidate Coverage Check
- **Evaluation:** Evaluates whether candidates featuring small lamps or doorway scenes are present.
- **Outcome:** Sufficient.

#### G. Controlled Recovery
- Not triggered.

#### H. Multi-Clue Matching
- Evaluates candidates compositionally against the co-occurrence of `diya` AND `gate`.
- Candidates depicting an entrance doorway with oil lamps are elevated over indoor table lamp photos.

#### I. Result Organization
- Preserves the chronological festival sequence (e.g., Diwali evening), allowing the user to see the photo in its event context.

#### J. Recognition Endpoint
- The user visually recognizes the entrance of their residence and the watchman lighting the lamp in Grid 2.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 4 (Candidate Discovery — Biometric Dependency).*
- **Why it breaks in baseline systems:** Systems that rely almost exclusively on biometric person clustering fail because infrequent service contacts (watchman, delivery person) are never labeled in the user's contact book. Without multi-path object/spatial fallback, the photo cannot be retrieved.

#### L. Evidence Traceability
- **Source:** [interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md) — **Episode 25** (Candidate 6, Task 25: `diya gate` retrieved the target in Grid 2 when face recognition was completely unavailable).

---

### Case Trace 5: "Progressive"

#### A. User Memory
The user remembers taking a photo of their car insurance bill to retain policy details: `"Progressive"`.

#### B. Memory Interpretation
- **`raw_input`:** `"Progressive"`
- **Populated V2 Frame:**
  ```json
  {
    "raw_input": "Progressive",
    "literal_text": [
      "Progressive"
    ]
  }
  ```
- **Interpretation Scope:** Understands that the user is searching for a literal text string printed on a document or physical item rather than asking a philosophical question or using an adjective.

#### C. Retrieval Signals
- **Generated Signals:**
  - *Literal Text Signal:* Exact alphanumeric token `"Progressive"`.
- **Distinction:** Segregated from conversational prompts or visual semantic embeddings.

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Literal Text Path:* Queries indexed in-image OCR text data specifically for the string `"Progressive"`.

#### E. Unified Candidate Pool
- Receives photographs containing printed or screen-displayed text matching `"Progressive"` (e.g., insurance letters, paper bills, declarations pages).

#### F. Candidate Coverage Check
- **Evaluation:** Checks if documents containing matching OCR text were identified.
- **Outcome:** Sufficient.

#### G. Controlled Recovery
- Not triggered.

#### H. Multi-Clue Matching
- Evaluates the prominence and match confidence of the text token within the candidate images.

#### I. Result Organization
- Organizes document photos with clear chronological timestamps so the user can identify the most recent policy statement.

#### J. Recognition Endpoint
- The user visually spots the insurance document with the blue Progressive logo/header and policy number.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 3 $\rightarrow$ Stage 4 (Conversational Prompt Misclassification).*
- **Why it breaks in baseline systems:** Monolithic conversational engines (e.g., Ask Photos) interpret `"Progressive"` as an abstract adjective or conversational topic, responding with chat dialog (*"I can't help with that"* or philosophical summaries) rather than executing an OCR scan of library images.

#### L. Evidence Traceability
- **Source:** [part1_combined_evidence.md](file:///d:/graduation%20project%203/part1_combined_evidence.md) / [research_summary.md](file:///d:/graduation%20project%203/research_summary.md) — **Reddit Case 5** (User searched `"Progressive"` for car insurance bill; conversational AI returned *"I can't help with that"*).

---

### Case Trace 6: "around 4 years ago"

#### A. User Memory
The user searches for a notarized document or lease agreement, recalling only a coarse elapsed timeframe: `"document around 4 years ago"`.

#### B. Memory Interpretation
- **`raw_input`:** `"document around 4 years ago"`
- **Populated V2 Frame:**
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
- **Interpretation Scope:** Preserves the natural hedging `"around"` in `raw_input` and categorizes the temporal anchor as a relative offset rather than an exact date.

#### C. Retrieval Signals
- **Generated Signals:**
  - *Visual Entity Signal:* `document` (text document, paperwork, receipt, letter).
  - *Temporal Constraint Signal:* Continuous multi-month/year interval centered around the calculated offset (e.g., spanning approximately 3.5 to 4.5 years prior to the current date).
- **Distinction:** Does not force an arbitrary calendar day or month.

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Temporal Path:* Gathers photos captured within the flexible historical window.
  - *Visual Entity Path:* Gathers document/paperwork images across the archive.

#### E. Unified Candidate Pool
- Receives candidate photos representing documents, letters, and forms captured during the estimated historical period.

#### F. Candidate Coverage Check
- **Evaluation:** Evaluates whether candidate documents exist within the open temporal window.
- **Outcome:** Sufficient.

#### G. Controlled Recovery
- Not triggered.

#### H. Multi-Clue Matching
- Evaluates the intersection of document visual characteristics and temporal proximity to the 4-year offset.
- Neutral treatment of unspecified dimensions: absence of location or person tags does not penalize candidates.

#### I. Result Organization
- Retains chronological sequence within that historical era, allowing the user to scan the documents filed around that time.

#### J. Recognition Endpoint
- The user visually recognizes the official stamp and header of the specific legal document.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 3 (Temporal Signal Generation — Rigid Timestamp Rejection).*
- **Why it breaks in baseline systems:** Traditional metadata search requires strict calendar inputs (e.g., `YYYY-MM-DD`). When conversational systems encounter relative phrases like `"around 4 years ago"`, they either refuse the query or fail to calculate the continuous date boundary.

#### L. Evidence Traceability
- **Source:** [interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md) — **Episode 10** (Candidate 2, Task 10: User recalled lease agreement from ~4 years prior; exact day and month were completely forgotten).

---

### Case Trace 7: "yellow truck" across 10 days

#### A. User Memory
The user recalls photographing a distinctive yellow utility truck multiple times throughout an extended road trip or work assignment: `"yellow truck"`.

#### B. Memory Interpretation
- **`raw_input`:** `"yellow truck"`
- **Populated V2 Frame:**
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
- **Interpretation Scope:** Binds the attribute `yellow` directly to the vehicle entity `truck`. Note that temporal range was not explicitly specified in the query text.

#### C. Retrieval Signals
- **Generated Signals:**
  - *Bound Entity-Attribute Signal:* `[Entity: truck | Attribute: yellow]`.
  - *Visual Entity Signal:* `truck` / `utility vehicle`.

#### D. Candidate Discovery (Initial Pass)
- **Activated Retrieval Paths:**
  - *Bound Entity-Attribute Path:* Gathers photos matching yellow trucks.
  - *Visual Entity Path:* Gathers general heavy utility vehicles.

#### E. Unified Candidate Pool (Initial Pass)
- Receives photos matching yellow trucks. However, the initial candidate retrieval pass returns candidates concentrated in only one or two isolated date clusters.

#### F. Candidate Coverage Check (TRIGGERED)
- **Evaluation:** The engine performs the conceptual check: *"Is the candidate set sufficiently broad and useful for evaluating the user's memory?"*
- **Outcome:** **INSUFFICIENT.**
- **Diagnostic Cause:** The initial search pass was overly constrained or prematurely truncated by a single-session search query, capturing photos from only 2 days while omitting 8 days of identical vehicle sightings spread across the collection.

#### G. Controlled Recovery (EXECUTED)
- **Broadening Strategy:**
  1. *Relaxing Secondary Visual Constraints:* Broadens the vehicle query to capture related commercial vehicle body types.
  2. *Querying Complementary Temporal Clusters:* Expands candidate gathering along the temporal timeline around the identified road trip / work project period.
- **Candidate Merging:** Newly discovered candidate photos across the other 8 days are merged directly into the unified candidate pool. Previously discovered candidates are preserved.

#### H. Multi-Clue Matching
- Evaluates all candidates in the expanded pool against the bound `[truck: yellow]` memory frame.
- High scores are assigned to yellow truck photos across all 10 separate days.

#### I. Result Organization
- Organizes the results by date and trip session, showing the recurring appearances of the yellow truck across the multi-day progression rather than an isolated 6-photo snapshot.

#### J. Recognition Endpoint
- The user can review the complete series of photos taken with the truck across the entire 10-day trip.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 4 (Candidate Discovery — The Few-Photos Truncation Bug).*
- **Why it breaks in baseline systems:** Commercial AI search engines frequently couple candidate gathering to a strict conversational presentation limit (e.g., returning only 6 photos or 2 days of media). Because there is no candidate coverage check, 80% of matching media is silently dropped.

#### L. Evidence Traceability
- **Source:** [part1_combined_evidence.md](file:///d:/graduation%20project%203/part1_combined_evidence.md) / [research_summary.md](file:///d:/graduation%20project%203/research_summary.md) — **Reddit Case 11** (User photographed yellow truck across 10 days; conversational search retrieved only 2 of the 10 days) and **Reddit Case 4** (6-photo ceiling on 400+ bird photos).

---

### Case Trace 8: Broad "wedding"

#### A. User Memory
The user searches broadly for family wedding photos: `"wedding"`.

#### B. Memory Interpretation
- **`raw_input`:** `"wedding"`
- **Populated V2 Frame:**
  ```json
  {
    "raw_input": "wedding",
    "events": {
      "event_name": "wedding"
    }
  }
  ```
- **Interpretation Scope:** Identifies a canonical event milestone (`wedding`). All other dimensions (people, clothing, year, setting) are unspecified.

#### C. Retrieval Signals
- **Generated Signals:**
  - *Event Signal:* `wedding` (ceremony, formal reception, traditional wedding attire).

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Event / Milestone Path:* Gathers photos tagged or clustered under wedding ceremonies.

#### E. Unified Candidate Pool
- Receives a broad collection of wedding photographs spanning multiple events and years across the user's library.

#### F. Candidate Coverage Check
- **Evaluation:** Evaluates if candidate wedding events were discovered across the library.
- **Outcome:** Sufficient.

#### G. Controlled Recovery
- Not triggered.

#### H. Multi-Clue Matching
- Evaluates candidate relevance against wedding visual markers. Because the query is broad, multiple wedding events score equally high.

#### I. Result Organization (CRITICAL STAGE FOR THIS CASE)
- **Conceptual Responsibility:** Retains event and chronological coherence. Rather than scattering individual photos based on uncalibrated visual similarity, results are organized into distinct event episodes with chronological landmarks.
- **Contextual Anchoring:** Preserves the multi-day connection so that when a user identifies a photo from a specific wedding (e.g., sister's 4-day wedding), surrounding rehearsal, ceremony, and reception photos remain accessible in context.

#### J. Recognition Endpoint
- The user visually recognizes the specific family wedding by its chronological cluster and visual landmarks, navigating into surrounding photos from that event.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 6 (Result Organization — Destruction of Chronological Context).*
- **Why it breaks in baseline systems:** Commercial systems sort by uncalibrated "Best Match", displaying two isolated photos from a 4-day wedding trip without allowing the user to view surrounding event photos. The user is forced to memorize the date, exit search, and scroll back through years of camera roll media.

#### L. Evidence Traceability
- **Source:** [part1_combined_evidence.md](file:///d:/graduation%20project%203/part1_combined_evidence.md) / [research_summary.md](file:///d:/graduation%20project%203/research_summary.md) — **Reddit Case 10** (User found 2 photos of nephew at sister's wedding, but could not see surrounding 4-day trip photos; forced to memorize date and scroll manually) and **Episode 02** (Broad wedding search flooding).

---

## 3. Cross-Case Patterns

A synthesis of the eight operating traces reveals consistent architectural patterns that justify the seven-stage pipeline:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        CROSS-STAGE ARCHITECTURAL NECESSITY                             │
├─────────────────────────┬──────────────────────────────────────────────────────────────┤
│ ARCHITECTURAL STAGE     │ WHEN IT MATTERS MOST & EVIDENCE PHENOMENON                   │
├─────────────────────────┼──────────────────────────────────────────────────────────────┤
│ 1. Memory Interpretation│ • Code-mixed vernacular syntax (Ep 06: "wali photo").        │
│                         │ • Relational social roles (Ep 05: "5 sisters").              │
│                         │ • Separates human intent from machine query syntax.          │
├─────────────────────────┼──────────────────────────────────────────────────────────────┤
│ 2. Signal Generation    │ • Literal text segregation (Reddit Case 5: "Progressive").   │
│                         │ • Approximate temporal offsets (Ep 10: "around 4 years ago").│
│                         │ • Derives searchable probes without altering user intent.    │
├─────────────────────────┼──────────────────────────────────────────────────────────────┤
│ 3. Multi-Path Discovery │ • Missing biometric clusters (Ep 25: "diya at the gate").    │
│                         │ • Prevents single-modality query bottlenecks.                │
├─────────────────────────┼──────────────────────────────────────────────────────────────┤
│ 4. Coverage Check &     │ • Artificial result ceilings (Reddit Case 4: 6-photo cap).   │
│    Controlled Recovery  │ • Multi-session truncation (Reddit Case 11: 2 of 10 days).   │
│                         │ • Protects recall before downstream scoring occurs.          │
├─────────────────────────┼──────────────────────────────────────────────────────────────┤
│ 5. Compositional        │ • Entity-attribute binding (Ep 13: "white bike").            │
│    Matching             │ • Prevents false-positive keyword flooding (Ep 22: "yellow").│
│                         │ • Soft satisfaction handles memory drift gracefully.         │
├─────────────────────────┼──────────────────────────────────────────────────────────────┤
│ 6. Result Organization  │ • Broad queries needing browsing (Reddit Case 10: "wedding").│
│                         │ • Preserves temporal landmarks for rapid human recognition.  │
└─────────────────────────┴──────────────────────────────────────────────────────────────┘
```

### 1. When Interpretation Matters
Interpretation is essential whenever users express memories using natural social relationships (`"sisters"`, `"cousin"`), possessive markers (`"my dog"`), or conversational code-mixing (`"wali photo"`). Without this layer, vernacular syntax acts as a poison pill that triggers total zero-result failures.

### 2. When Signal Generation Matters
Signal Generation is distinct from interpretation. It is critical when an interpreted concept cannot be directly queried in a physical index:
- Literal text must be isolated from conversational dialog prompts.
- Kinship roles must generate candidate demographic search probes.
- Relative temporal offsets must generate continuous interval constraints.

### 3. When Multi-Path Candidate Discovery Matters
Single-path search fails whenever the primary expected modality is absent in the collection metadata (e.g., face recognition failing for infrequent acquaintances in Episode 25). Multi-path discovery ensures that spatial, object, temporal, and action paths can independently gather candidates into the unified pool.

### 4. When Candidate Coverage Check & Controlled Recovery Matter
These mechanisms are vital for protecting recall. When initial discovery is prematurely truncated by narrow query probes or artificial system limits (e.g., Reddit Case 4 returning 6 of 400+ birds, or Reddit Case 11 returning 2 of 10 days of trucks), the coverage check detects the gap and triggers controlled broadening before final scoring.

### 5. When Compositional Matching Matters
Compositional evaluation is indispensable whenever queries involve entity-attribute combinations (`"white bike"`, `"yellow suit"`, `"family yellow"`). Independent keyword scoring floods results with unrelated items sharing a single attribute; compositional binding ensures attributes are scored directly on the host entity.

### 6. When Result Organization Matters
Result organization is crucial for visual recognition and navigation. When queries are broad (`"wedding"`), uncalibrated relevance sorting scatters photos across time, disorienting the user. Retaining chronological and event context allows users to navigate surrounding event moments.

### 7. How Sparse and Uncertain Memory Is Handled
Throughout all eight traces:
- **Missing dimensions are treated as neutral wildcards, never as exclusionary filters.**
- **Approximate time is mapped to flexible continuous intervals, never to rigid calendar days.**
- **Verbatim uncertainty terms are preserved in `raw_input` without forcing arbitrary confidence numbers.**

---

## 4. Architecture-to-Research Traceability Matrix

The matrix below provides complete traceability between the empirical research cases and the conceptual architectural responsibilities:

| Evidence Case | Memory Representation | Retrieval Signal | Discovery Path | Coverage Issue | Matching Responsibility | Organization Responsibility |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **"5 sisters"** (Ep 05) | `people: [{role: "sister", count: 5}]` | Relational demographic probes (`count: 5`) | Relational-derived & visual entity paths | None (sufficient initial group candidates) | Demographic & group size congruence | Connects to surrounding family gathering context |
| **"rohtang ice wali"** (Ep 06/07) | `objects: ["ice"]`, `spatial_setting: "rohtang"` | Geographic landmark & visual ice/snow | Spatial & visual entity paths | None (sufficient landscape candidates) | Compositional spatial + object co-occurrence | Preserves trip sequence and scenic stop context |
| **"white bike"** (Ep 13) | `objects: [{name: "bike", attributes: ["white"]}]` | Bound `[bike: white]` & fallback entity `bike` | Bound entity-attribute & visual entity paths | None (sufficient vehicle candidates) | Entity-attribute binding (color on vehicle) | Retains daily activity context |
| **"diya at the gate"** (Ep 25) | `objects: ["diya"]`, `spatial_setting: "gate"` | Co-occurring visual lamp & entrance spatial | Multi-path fallback (spatial + object) | None (bypasses missing face clusters) | Object + spatial co-occurrence | Retains festival evening timeline |
| **"Progressive"** (Reddit Case 5) | `literal_text: ["Progressive"]` | Exact alphanumeric token | Dedicated in-image OCR text path | None (sufficient OCR document hits) | Literal token match prominence | Chronological document filing order |
| **"around 4 years ago"** (Ep 10) | `objects: ["document"]`, `temporal: RELATIVE_OFFSET` | Continuous multi-month/year interval | Temporal interval & visual document paths | None (sufficient historical documents) | Intersection of document type and time interval | Chronological legal/lease filing sequence |
| **"yellow truck"** (Reddit Case 11) | `objects: [{name: "truck", attributes: ["yellow"]}]` | Bound `[truck: yellow]` & vehicle body | Bound entity-attribute & temporal paths | **Insufficient:** candidates concentrated in only 2 of 10 days | Compositional vehicle-color congruence across all days | Multi-day trip session organization |
| **Broad "wedding"** (Ep 02 / Reddit Case 10) | `events: {event_name: "wedding"}` | Canonical event milestone signal | Event / milestone gathering path | None (sufficient ceremony candidates) | Event visual markers (equal high score) | **Critical:** Retains 4-day event landmarks for contextual browsing |

---

## 5. Part 1 Readiness Check

The conceptual architecture and operating specification are evaluated against the seven core readiness questions:

### 1. Can the architecture represent the major memory types observed in the evidence?
**YES.** The V2 Memory Representation Schema provides structured, non-premature representations for social kinship roles (`people`), milestone occasions (`events`), salient physical props (`objects`), bound visual attributes, dynamic physical activities (`actions`), approximate and relative time (`temporal`), in-image alphanumeric text (`literal_text`), and geographic landscapes (`spatial_setting`), while preserving `raw_input` verbatim.

### 2. Can each major failure case be mapped to a specific architectural responsibility?
**YES.** Every observed failure across our 25 interview tasks and 61 public review cases maps directly to an identifiable stage failure:
- Kinship failure $\rightarrow$ Memory Interpretation & Retrieval Signal Generation.
- Vernacular failure $\rightarrow$ Memory Interpretation (Raw Input Preservation).
- Disconnected color flooding $\rightarrow$ Multi-Clue Matching (Compositional Binding).
- Chatbot prompt refusal $\rightarrow$ Literal Text Retrieval Path.
- The 6-photo truncation ceiling $\rightarrow$ Candidate Discovery & Candidate Coverage Checking.
- Contextual disorientation $\rightarrow$ Result Organization.

### 3. Can the architecture explain how candidate recall is protected?
**YES.** Recall is protected by:
- Decoupling Candidate Discovery from downstream ranking.
- Gathering candidates across multiple specialized retrieval paths into a unified pool.
- Implementing an explicit **Candidate Coverage Check** to detect under-retrieval.
- Executing **Controlled Recovery / Broadening** to merge complementary candidates before final scoring.

### 4. Can the architecture explain how multi-clue memories are evaluated?
**YES.** The Multi-Clue Matching Layer evaluates candidates against the combined memory frame compositionally, ensuring that visual attributes are scored as properties bound directly to host entities rather than as independent keywords.

### 5. Can the architecture handle sparse and uncertain memories?
**YES.** The architecture explicitly mandates that unspecified dimensions are treated as neutral wildcards rather than negative filters, approximate temporal expressions are mapped to continuous flexible intervals, and linguistic hedging is preserved without artificial numeric scoring.

### 6. Can the architecture explain literal text retrieval separately?
**YES.** The Literal Text Retrieval Path routes alphanumeric tokens directly to an in-image text matching channel, isolating document and meme queries from conversational dialog prompts.

### 7. Are there any remaining conceptual gaps that BLOCK Part 1 completion?
**NO.** All major failure modes, memory dimensions, retrieval paths, and conceptual responsibilities have been formalized, cross-checked against empirical evidence, and stress-tested. Technical implementation choices (models, databases, formulas) and interface designs remain deliberately and appropriately deferred.

---

### Part 1 Architectural Sign-Off

$$\mathbf{CONCLUSION:}\ \text{Part 1 conceptual Discovery Engine is ready to move from architecture into experimental/prototyping work.}$$

This operating specification, alongside [part1_discovery_engine_architecture_final.md](file:///d:/graduation%20project%203/part1_discovery_engine_architecture_final.md) and [part1_memory_representation_schema_v2.md](file:///d:/graduation%20project%203/part1_memory_representation_schema_v2.md), forms the complete, locked conceptual foundation for Part 1. No implementation code, database selections, or Part 5 UI wireframing should be initiated until prototyping experimental parameters are formally established.
