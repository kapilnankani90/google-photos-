# Part 1 — Discovery Engine Operating Specification (Final)

## 1. Document Objective & Scope

The purpose of this document is to translate the **LOCKED** conceptual architecture defined in [part1_discovery_engine_architecture_final.md](file:///d:/graduation%20project%203/part1_discovery_engine_architecture_final.md) and the schema defined in [part1_memory_representation_schema_v2.md](file:///d:/graduation%20project%203/part1_memory_representation_schema_v2.md) into concrete, end-to-end operational traces using representative, real-world evidence cases.

$$\mathbf{PROJECT\ ANCHOR:}\ \text{Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching.}$$

This specification demonstrates how the seven-stage conceptual pipeline is designed to behave when presented with human memory expressions that are imperfect, colloquial, relational, sparse, or approximate.

> [!IMPORTANT]
> **Conceptual Specification Boundaries & Evidence Discipline:**
> - This document is **not** an implementation or software specification.
> - It does **not** choose machine learning models, LLMs, vision backends, vector indexes, databases, or API protocols.
> - It does **not** design user interfaces, layouts, or wireframes.
> - It distinguishes clearly between:
>   - **OBSERVED:** Documented user behaviors and failure modes from research interviews and public evidence.
>   - **EXPECTED / HYPOTHESIZED:** The conceptual behavior the Discovery Engine is designed to exhibit, subject to later experimental validation.
> - It does **not** present conceptual design behavior as empirical validation or proven results.

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
- **Interpretation Scope:** Interpretation answers *"What does the user mean?"* It identifies a relational kinship role (`sister`) and an explicit cardinality (`count: 5`). It preserves `raw_input` verbatim and does not force premature conversion.

#### C. Retrieval Signals
- **Conceptual Responsibility:** Derives searchable representations from interpreted meaning.
- **Hypothesized Retrieval Signals:**
  - *Relational-Derived Demographic Signals:* Candidate concepts for groups of five female individuals.
  - *Cardinality Constraint:* Group count of 5 individuals.
- **Distinction from Interpretation:** Interpretation preserves the social relationship (`sister`); Signal Generation creates candidate visual search probes because personal photo libraries rarely index private family genealogical trees.

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Relational-Derived Path:* Active (queries media containing demographic clusters matching the group size and visual primitives).
  - *Visual Entity Path:* Active (queries multi-person group portraits).
- Unactivated paths (Temporal, Spatial, Action, Literal Text) remain neutral.

#### E. Unified Candidate Pool
- **Expected Content:** The candidate pool should receive photographs containing groups of people, particularly groups of approximately five female individuals or multi-person family portraits.

#### F. Candidate Coverage Check
- **Evaluation:** The engine evaluates whether the candidate pool contains multi-person group photographs matching the cardinality cue.
- **Expected Conceptual Behavior:** Initial candidate coverage should be sufficient for this case, subject to later experimental validation.

#### G. Controlled Recovery
- **Expected Flow:** Not triggered under baseline expectations; reserved for cases where candidate coverage is judged insufficient.

#### H. Multi-Clue Matching
- **Expected Evaluation:** Evaluates candidate photos against the populated frame compositionally:
  - Higher scores should be assigned to photos matching both group cardinality (`count: 5`) and demographic congruence.
  - The absence of temporal, spatial, or action specifications is treated as neutral (wildcard).

#### I. Result Organization
- **Expected Behavior:** Retains contextual coherence by keeping candidate group portraits connected to their surrounding event timeline (e.g., family gatherings or holiday moments) rather than dispersing them across disconnected rows.

#### J. Recognition Endpoint
- **Expected Conceptual Behavior:** The target photo should become identifiable within the candidate set alongside surrounding family context, allowing the user to recognize the gathering once relevant demographic and group signals are retrieved.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 2 $\rightarrow$ Stage 3 (Interpretation to Retrieval Signal Generation).*
- **Why it breaks in baseline systems:** In the documented baseline behavior, systems search literally for the label `"sister"` in metadata or vision tags. When underlying image indexers output demographic labels (`"girl"`, `"woman"`) rather than kinship roles, direct search returns zero results (*"No results found"*).

#### L. Evidence Traceability
- **Source:** [interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md) — **Episode 05** (Candidate 2, Task 5: Observed that `5 sisters` returned 0 results; manual conversion to `5 girls` retrieved target at Rank 1).

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
- **Hypothesized Retrieval Signals:**
  - *Spatial Setting Signal:* Geographic landmark / region concept (`Rohtang`, mountainous snow terrain).
  - *Visual Entity Signal:* Physical visual element (`ice`, `snow`).
- **Distinction:** Vernacular noise is stripped from the searchable signals while preserved in `raw_input`.

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Spatial / Environmental Path:* Searches geographic metadata and landscape scene tags for Rohtang or high-altitude terrain.
  - *Visual Entity Path:* Searches for visual snow/ice textures and winter outdoor settings.

#### E. Unified Candidate Pool
- **Expected Content:** Should receive candidate outdoor photos taken at high-altitude mountain passes, snowy landscapes, and geotagged or visually tagged Rohtang media.

#### F. Candidate Coverage Check
- **Evaluation:** Evaluates whether candidates representing the snowy mountain setting enter the pool.
- **Expected Conceptual Behavior:** Initial candidate coverage should be sufficient for this case, subject to later experimental validation.

#### G. Controlled Recovery
- **Expected Flow:** Not triggered under baseline expectations.

#### H. Multi-Clue Matching
- **Expected Evaluation:** Evaluates candidates compositionally against both `spatial_setting: "rohtang"` and `objects: ["ice"]`, prioritizing photos that satisfy both the location context and the salient visual snow element.

#### I. Result Organization
- **Expected Behavior:** Retains chronological and trip coherence, keeping photos from the mountain excursion grouped together so the user can identify the specific roadside or scenic stop.

#### J. Recognition Endpoint
- **Expected Conceptual Behavior:** The target photograph should become recognizable within the retrieved mountain trip context once vernacular particles are isolated and geographic/snow signals are evaluated.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 2 (Memory Interpretation — Vernacular Syntax Rejection).*
- **Why it breaks in baseline systems:** In the documented baseline behavior, search bars treat colloquial Hindi postpositions (`wali`, `photo`) as literal query keywords, causing lookup failure and returning an empty result screen.

#### L. Evidence Traceability
- **Source:** [interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md) — **Episode 06** (Candidate 2, Task 6: Observed that `rohtang ki ice wali photo` failed on `wali photo`; stripping to `rohtang ice pic` succeeded) and **Episode 07** (`marble cake wali photo`).

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
- **Hypothesized Retrieval Signals:**
  - *Bound Entity-Attribute Signal:* `[Entity: bike | Attribute: white]`.
  - *Fallback Entity Signal:* `bike` (unbound, to ensure candidate breadth).

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Bound Entity-Attribute Path:* Gathers photos containing white motorcycles or bicycles.
  - *Visual Entity Path:* Gathers general two-wheeled vehicles to protect against partial attribute tagging failures.

#### E. Unified Candidate Pool
- **Expected Content:** Should receive candidate photographs featuring motorcycles and bicycles, with priority given to those exhibiting white or light-colored vehicle bodies.

#### F. Candidate Coverage Check
- **Evaluation:** Evaluates whether two-wheeled vehicle candidates were gathered.
- **Expected Conceptual Behavior:** Initial candidate coverage should be sufficient for this case, subject to later experimental validation.

#### G. Controlled Recovery
- **Expected Flow:** Not triggered under baseline expectations.

#### H. Multi-Clue Matching
- **Compositional Responsibility:** Specifically evaluates `white` as a property of the `bike`.
- Prevents false-positive flooding: a candidate photo containing a black motorcycle next to a person in a white shirt should be down-ranked relative to a candidate where the white color is localized directly on the vehicle.

#### I. Result Organization
- **Expected Behavior:** Retains surrounding context from the day the motorcycle ride occurred.

#### J. Recognition Endpoint
- **Expected Conceptual Behavior:** The photograph of the family member on the white motorcycle should become identifiable near the top of the evaluated candidate set if the bound color attribute is evaluated directly on the vehicle.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 5 (Multi-Clue Matching — Disconnected Attribute Scoring).*
- **Why it breaks in baseline systems:** In the documented baseline behavior, uncoordinated bag-of-words systems score `white` and `bike` independently, flooding top ranks with hundreds of photos containing unrelated white objects (shirts, walls, backgrounds) alongside dark vehicles.

#### L. Evidence Traceability
- **Source:** [interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md) — **Episode 13** (Candidate 3, Task 13: Observed that `white bike` retrieved the target at Position 1–3 because color was bound directly to the vehicle).

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
- **Interpretation Scope:** Extracts the salient festival object (`diya`) and spatial architectural boundary (`gate`). Demonstrates memory sparsity: the person (`watchman`) was not explicitly named in the query text.

#### C. Retrieval Signals
- **Hypothesized Retrieval Signals:**
  - *Visual Entity Signal:* `diya` (oil lamp, small flame).
  - *Spatial Setting Signal:* `gate` (entrance gate, doorway, threshold).
  - *Co-occurrence Context:* Evening lighting / festival environment.

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Visual Entity Path:* Gathers photos with flame/diya tags or visual features.
  - *Spatial / Environmental Path:* Gathers photos taken near entry gates and doorways.
- Multi-path gathering is designed to enable candidate retrieval even when biometric face recognition is unindexed for this infrequent contact.

#### E. Unified Candidate Pool
- **Expected Content:** Should receive candidate photos of outdoor festival lighting, lamps near doorways, and entrance gate scenes.

#### F. Candidate Coverage Check
- **Evaluation:** Evaluates whether candidates featuring small lamps or doorway scenes are present.
- **Expected Conceptual Behavior:** Initial candidate coverage should be sufficient for this case, subject to later experimental validation.

#### G. Controlled Recovery
- **Expected Flow:** Not triggered under baseline expectations.

#### H. Multi-Clue Matching
- **Expected Evaluation:** Evaluates candidate photos compositionally for the co-occurrence of entrance/doorway context and festive oil lamps. Candidates depicting an entrance doorway with oil lamps should be elevated over indoor table lamp photos.

#### I. Result Organization
- **Expected Behavior:** Retains the chronological festival sequence (Diwali evening), allowing the user to view the photo in its event context.

#### J. Recognition Endpoint
- **Expected Conceptual Behavior:** The target photo should become discoverable within the evening festival context through co-occurring object and spatial cues, even in the complete absence of biometric identity clustering for the infrequent acquaintance.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 4 (Candidate Discovery — Biometric Dependency).*
- **Why it breaks in baseline systems:** In the documented baseline behavior, systems relying primarily on biometric clustering fail when a photo depicts an infrequent contact who is unindexed in face albums. Without multi-path object/spatial fallback, the photo cannot be retrieved.

#### L. Evidence Traceability
- **Source:** [interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md) — **Episode 25** (Candidate 6, Task 25: Observed that `diya gate` retrieved the target in Grid 2 when face recognition was completely unavailable).

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
- **Interpretation Scope:** Interprets the query as remembered literal text appearing on an object or document rather than a conversational prompt or descriptive adjective.

#### C. Retrieval Signals
- **Hypothesized Retrieval Signals:**
  - *Literal Text Signal:* Exact alphanumeric token `"Progressive"`.
- **Architectural Requirement:** Literal text must be retrievable from text appearing within images, segregated from conversational dialog prompts.

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Literal Text Path:* Searches image content for the remembered literal text `"Progressive"`.

#### E. Unified Candidate Pool
- **Expected Content:** Should receive candidate images containing printed, stamped, or screen-displayed text matching `"Progressive"` (e.g., insurance letters, paper bills, declarations pages).

#### F. Candidate Coverage Check
- **Evaluation:** Evaluates whether documents or images containing the remembered literal text were gathered.
- **Expected Conceptual Behavior:** Initial candidate coverage should be sufficient for this case, subject to later experimental validation.

#### G. Controlled Recovery
- **Expected Flow:** Not triggered under baseline expectations.

#### H. Multi-Clue Matching
- **Expected Evaluation:** Evaluates the prominence and match completeness of the literal text token within candidate images.

#### I. Result Organization
- **Expected Behavior:** Organizes document images chronologically so the user can easily identify the most recent policy statement.

#### J. Recognition Endpoint
- **Expected Conceptual Behavior:** The insurance document should become identifiable within the candidate set once literal text is matched against in-image text rather than processed as conversational dialog.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 3 $\rightarrow$ Stage 4 (Conversational Prompt Misclassification).*
- **Why it breaks in baseline systems:** In the observed baseline cases (e.g., Ask Photos in Reddit Case 5), conversational search experiences interpreted `"Progressive"` as an abstract adjective or conversational topic, responding with conversational refusals (*"I can't help with that"*) rather than searching for text appearing within images.

#### L. Evidence Traceability
- **Source:** [part1_combined_evidence.md](file:///d:/graduation%20project%203/part1_combined_evidence.md) / [research_summary.md](file:///d:/graduation%20project%203/research_summary.md) — **Reddit Case 5** (Observed user searched `"Progressive"` for car insurance bill; conversational search returned *"I can't help with that"*).

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
- **Hypothesized Retrieval Signals:**
  - *Visual Entity Signal:* `document` (text document, paperwork, receipt, letter).
  - *Temporal Constraint Signal:* Continuous multi-month/year interval centered around the calculated offset (e.g., spanning approximately 3.5 to 4.5 years prior to the current date).
- **Distinction:** Avoids forcing an arbitrary calendar day or month.

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Temporal Path:* Gathers photos captured within the flexible historical window.
  - *Visual Entity Path:* Gathers document/paperwork images across the archive.

#### E. Unified Candidate Pool
- **Expected Content:** Should receive candidate images representing paperwork, documents, and forms captured during the estimated historical period.

#### F. Candidate Coverage Check
- **Evaluation:** Evaluates whether candidate documents are gathered within the continuous historical interval.
- **Expected Conceptual Behavior:** Initial candidate coverage should be sufficient for this case, subject to later experimental validation.

#### G. Controlled Recovery
- **Expected Flow:** Not triggered under baseline expectations.

#### H. Multi-Clue Matching
- **Expected Evaluation:** Evaluates the intersection of document visual characteristics and temporal proximity to the 4-year offset. Absence of location or person tags is treated as neutral (wildcard).

#### I. Result Organization
- **Expected Behavior:** Retains chronological sequence within that historical era, allowing the user to scan the documents filed around that time.

#### J. Recognition Endpoint
- **Expected Conceptual Behavior:** The specific document should become recognizable within the open temporal interval window without requiring the user to recall an exact day or month.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 3 (Temporal Signal Generation — Rigid Timestamp Rejection).*
- **Why it breaks in baseline systems:** In the documented baseline behavior, search filters require strict calendar dates (`YYYY-MM-DD`). When conversational systems encounter relative phrases like `"around 4 years ago"`, they either refuse the query or fail to calculate the continuous date boundary.

#### L. Evidence Traceability
- **Source:** [interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md) — **Episode 10** (Candidate 2, Task 10: Observed user recalled lease agreement from ~4 years prior; exact day and month were completely forgotten).

---

### Case Trace 7: "yellow truck" across 10 days

#### A. User Memory
The user recalls photographing a distinctive yellow utility truck multiple times throughout an extended road trip or work project: `"yellow truck"`.

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
- **Interpretation Scope:** Binds the attribute `yellow` directly to the vehicle entity `truck`. Temporal range was not explicitly specified in the query text.

#### C. Retrieval Signals
- **Hypothesized Retrieval Signals:**
  - *Bound Entity-Attribute Signal:* `[Entity: truck | Attribute: yellow]`.
  - *Visual Entity Signal:* `truck` / `utility vehicle`.

#### D. Candidate Discovery (Initial Pass)
- **Activated Retrieval Paths:**
  - *Bound Entity-Attribute Path:* Gathers photos matching yellow trucks.
  - *Visual Entity Path:* Gathers general utility and work vehicles.

#### E. Unified Candidate Pool (Initial Pass)
- **Expected Content:** Receives candidate photos matching yellow trucks. However, the initial retrieval probe may return candidates concentrated in only one or two isolated date clusters.

#### F. Candidate Coverage Check (TRIGGERED)
- **Evaluation:** The engine performs the conceptual check: *"Is the candidate set sufficiently broad and useful for evaluating the user's memory?"*
- **Expected Conceptual Behavior:** Initial candidate coverage is judged insufficient due to candidate concentration in an isolated session while ignoring broader multi-day media, prompting controlled recovery subject to later experimental validation.
- **Diagnostic Cause:** Initial search probe was overly constrained or prematurely truncated by a single-session search limit, capturing photos from only 2 days while omitting 8 days of identical vehicle sightings spread across the collection.

#### G. Controlled Recovery (Hypothesized Flow)
- **Broadening Strategy:**
  1. *Relaxing Secondary Visual Constraints:* Broadens the vehicle probe to capture related utility and work vehicle body types.
  2. *Querying Complementary Temporal Clusters:* Expands candidate gathering along the temporal timeline around the identified project period.
- **Candidate Merging:** Newly discovered candidate photos across the other 8 days are merged directly into the unified candidate pool. Previously discovered candidates are preserved.

#### H. Multi-Clue Matching
- **Expected Evaluation:** Compositionally evaluates all candidates in the expanded pool against the bound `[truck: yellow]` frame, assigning high scores to matching yellow truck photos across all 10 days.

#### I. Result Organization
- **Expected Behavior:** Organizes results by date and trip session, showing the progression of the vehicle appearances across the multi-day event rather than an isolated snapshot.

#### J. Recognition Endpoint
- **Expected Conceptual Behavior:** Photographs of the yellow truck across the multi-day trip should enter the candidate pool and become discoverable once controlled recovery broadens the search beyond initial single-session truncation.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 4 (Candidate Discovery — The Few-Photos Truncation Bug).*
- **Why it breaks in baseline systems:** In the evidence collected for this project (e.g., Reddit Cases 4 and 11), conversational search experiences coupled candidate gathering to a strict presentation limit (returning only 6 photos or 2 days of media). Without a candidate coverage check, matching media across other sessions was silently omitted.

#### L. Evidence Traceability
- **Source:** [part1_combined_evidence.md](file:///d:/graduation%20project%203/part1_combined_evidence.md) / [research_summary.md](file:///d:/graduation%20project%203/research_summary.md) — **Reddit Case 11** (Observed user photographed yellow truck across 10 days; conversational search retrieved only 2 of the 10 days) and **Reddit Case 4** (6-photo ceiling on 400+ bird photos).

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
- **Hypothesized Retrieval Signals:**
  - *Event Signal:* `wedding` (ceremony, formal reception, traditional wedding attire).

#### D. Candidate Discovery
- **Activated Retrieval Paths:**
  - *Event / Milestone Path:* Gathers photos tagged or clustered under wedding ceremonies.

#### E. Unified Candidate Pool
- **Expected Content:** Should receive a broad collection of candidate wedding photographs spanning multiple events and years across the user's collection.

#### F. Candidate Coverage Check
- **Evaluation:** Evaluates whether wedding event candidates were discovered.
- **Expected Conceptual Behavior:** Initial candidate coverage should be sufficient for this case, subject to later experimental validation.

#### G. Controlled Recovery
- **Expected Flow:** Not triggered under baseline expectations.

#### H. Multi-Clue Matching
- **Expected Evaluation:** Evaluates candidate relevance against wedding visual markers. Because the query is broad, multiple wedding events score equally high.

#### I. Result Organization (Critical Stage for This Case)
- **Conceptual Responsibility:** Retains event and chronological coherence. Rather than scattering individual photos based on uncalibrated visual similarity, results are organized into distinct event episodes with chronological landmarks.
- **Contextual Anchoring:** Preserves multi-day connections so that when a user identifies a photo from a specific wedding (e.g., sister's 4-day wedding), surrounding ceremony, rehearsal, and reception photos remain accessible in context.

#### J. Recognition Endpoint
- **Expected Conceptual Behavior:** The user should be able to identify the specific wedding through chronological and landmark event clustering, retaining contextual connections to surrounding photos from that occasion.

#### K. Diagnostic Failure Mode
- **Vulnerable Stage:** *Stage 6 (Result Organization — Destruction of Chronological Context).*
- **Why it breaks in baseline systems:** In the documented baseline behavior (e.g., Reddit Case 10), systems sorted by uncalibrated "Best Match", displaying isolated photos from an extended event without providing contextual navigation to surrounding photos. The user was forced to memorize the date, exit search, and manually scroll through years of camera roll media.

#### L. Evidence Traceability
- **Source:** [part1_combined_evidence.md](file:///d:/graduation%20project%203/part1_combined_evidence.md) / [research_summary.md](file:///d:/graduation%20project%203/research_summary.md) — **Reddit Case 10** (Observed user found 2 photos of nephew at sister's wedding, but could not see surrounding 4-day trip photos; forced to memorize date and scroll manually) and **Episode 02** (Broad wedding search flooding).

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
Interpretation is essential whenever users express memories using natural social relationships (`"sisters"`, `"cousin"`), possessive markers (`"my dog"`), or conversational code-mixing (`"wali photo"`). In documented baseline behavior, without this layer, vernacular syntax acts as a poison pill that triggers total zero-result failures.

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
- **Missing dimensions are treated as neutral wildcards, avoiding exclusionary filtering.**
- **Approximate time is mapped to flexible continuous intervals, avoiding rigid calendar date constraints.**
- **Verbatim uncertainty terms are preserved in `raw_input` without forcing arbitrary confidence numbers.**

---

## 4. Architecture-to-Research Traceability Matrix

The matrix below provides complete traceability between the empirical research cases and the conceptual architectural responsibilities:

| Evidence Case | Memory Representation | Retrieval Signal | Discovery Path | Coverage Check (Hypothesized) | Matching Responsibility | Organization Responsibility |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **"5 sisters"** (Ep 05) | `people: [{role: "sister", count: 5}]` | Relational demographic probes (`count: 5`) | Relational-derived & visual entity paths | Initial candidate coverage should be sufficient | Demographic & group size congruence | Connects to surrounding family gathering context |
| **"rohtang ice wali"** (Ep 06/07) | `objects: ["ice"]`, `spatial_setting: "rohtang"` | Geographic landmark & visual ice/snow | Spatial & visual entity paths | Initial candidate coverage should be sufficient | Compositional spatial + object co-occurrence | Preserves trip sequence and scenic stop context |
| **"white bike"** (Ep 13) | `objects: [{name: "bike", attributes: ["white"]}]` | Bound `[bike: white]` & fallback entity `bike` | Bound entity-attribute & visual entity paths | Initial candidate coverage should be sufficient | Entity-attribute binding (color on vehicle) | Retains daily activity context |
| **"diya at the gate"** (Ep 25) | `objects: ["diya"]`, `spatial_setting: "gate"` | Co-occurring visual lamp & entrance spatial | Multi-path fallback (spatial + object) | Initial candidate coverage should be sufficient | Object + spatial co-occurrence | Retains festival evening timeline |
| **"Progressive"** (Reddit Case 5) | `literal_text: ["Progressive"]` | Exact alphanumeric token | Dedicated in-image text path | Initial candidate coverage should be sufficient | Literal token match prominence | Chronological document filing order |
| **"around 4 years ago"** (Ep 10) | `objects: ["document"]`, `temporal: RELATIVE_OFFSET` | Continuous multi-month/year interval | Temporal interval & visual document paths | Initial candidate coverage should be sufficient | Intersection of document type and time interval | Chronological legal/lease filing sequence |
| **"yellow truck"** (Reddit Case 11) | `objects: [{name: "truck", attributes: ["yellow"]}]` | Bound `[truck: yellow]` & vehicle body | Bound entity-attribute & temporal paths | **Insufficient:** candidates concentrated in only 2 of 10 days; triggers controlled broadening | Compositional vehicle-color congruence across all days | Multi-day trip session organization |
| **Broad "wedding"** (Ep 02 / Reddit Case 10) | `events: {event_name: "wedding"}` | Canonical event milestone signal | Event / milestone gathering path | Initial candidate coverage should be sufficient | Event visual markers (equal high score) | **Critical:** Retains event landmarks for contextual browsing |

---

## 5. Part 1 Readiness Check

The conceptual architecture and operating specification are evaluated against the seven core readiness questions:

### 1. Can the architecture represent the major memory types observed in the evidence?
**YES.** The V2 Memory Representation Schema provides structured, non-premature representations for social kinship roles (`people`), milestone occasions (`events`), salient physical props (`objects`), bound visual attributes, dynamic physical activities (`actions`), approximate and relative time (`temporal`), in-image alphanumeric text (`literal_text`), and geographic landscapes (`spatial_setting`), while preserving `raw_input` verbatim.

### 2. Can each major failure case be mapped to a specific architectural responsibility?
**YES.** Every observed failure across our 25 interview tasks and 61 public review cases maps directly to an identifiable stage responsibility:
- Kinship failure $\rightarrow$ Memory Interpretation & Retrieval Signal Generation.
- Vernacular failure $\rightarrow$ Memory Interpretation (Raw Input Preservation).
- Disconnected color flooding $\rightarrow$ Multi-Clue Matching (Compositional Binding).
- Chatbot prompt refusal $\rightarrow$ Literal Text Retrieval Path.
- The 6-photo truncation ceiling $\rightarrow$ Candidate Discovery & Candidate Coverage Checking.
- Contextual disorientation $\rightarrow$ Result Organization.

### 3. Can the architecture explain how candidate recall is protected?
**YES.** The architecture is designed to protect recall by:
- Decoupling Candidate Discovery from downstream ranking.
- Gathering candidates across multiple specialized retrieval paths into a unified pool.
- Introducing a conceptual **Candidate Coverage Check** to detect under-retrieval.
- Enabling **Controlled Recovery / Broadening** to merge complementary candidates before final scoring.

### 4. Can the architecture explain how multi-clue memories are evaluated?
**YES.** The Multi-Clue Matching Layer evaluates candidates against the combined memory frame compositionally, ensuring that visual attributes are scored as properties bound directly to host entities rather than as independent keywords.

### 5. Can the architecture handle sparse and uncertain memories?
**YES.** The architecture explicitly mandates that unspecified dimensions are treated as neutral wildcards rather than negative filters, approximate temporal expressions are mapped to continuous flexible intervals, and linguistic hedging is preserved without artificial numeric scoring.

### 6. Can the architecture explain literal text retrieval separately?
**YES.** The Literal Text Retrieval Path establishes the requirement that literal text must be retrievable from text appearing within images, routing alphanumeric tokens directly to an in-image text matching channel to isolate document and sign queries from conversational dialog prompts.

### 7. Are there any remaining conceptual gaps that BLOCK Part 1 completion?
**NO.** All major failure modes, memory dimensions, retrieval paths, and conceptual responsibilities have been formalized, cross-checked against empirical evidence, and stress-tested. Technical implementation choices (models, databases, formulas) and interface designs remain deliberately and appropriately deferred.

---

### Part 1 Architectural Sign-Off

$$\mathbf{CONCLUSION:}\ \text{Part 1 conceptual Discovery Engine is ready to move from architecture into experimental/prototyping work.}$$

This operating specification, alongside [part1_discovery_engine_architecture_final.md](file:///d:/graduation%20project%203/part1_discovery_engine_architecture_final.md) and [part1_memory_representation_schema_v2.md](file:///d:/graduation%20project%203/part1_memory_representation_schema_v2.md), forms the complete, locked conceptual foundation for Part 1. This means the conceptual foundation is complete; it does not mean the architecture has already been experimentally validated. No implementation code, database selections, or Part 5 UI wireframing should be initiated until prototyping experimental parameters are formally established.
