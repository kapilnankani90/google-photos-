# Part 2 — Business Metric Decomposition

---

## 1. Top-Level Metric Definition

### Exact Metric Formulation
The project anchor and strategic objective for this initiative is defined as:

$$\mathbf{Top\text{-}Level\ Metric:}\ \text{Percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching.}$$

### Conceptual Definition
This metric evaluates human-task completion under conditions of incomplete episodic recall. It measures the proportion of users with an imperfectly remembered photo target who, upon initiating a retrieval attempt, reach successful identification and retrieval of that specific target.

### Formal Mathematical Structure

$$\text{Top-Level Business Metric} = \frac{\text{Successful Eligible Retrievals}}{\text{Eligible Retrieval Attempts}} = \frac{N_{\text{successful}}}{D_{\text{eligible}}} \times 100$$

#### Denominator ($D_{\text{eligible}}$): Eligible User Retrieval Population
- **Conceptual Definition:** The count of unique users who initiate a retrieval attempt with a specific remembered target photo in mind, but whose memory does not contain a sufficiently precise description to uniquely identify the target using conventional searchable descriptors.
- **Inclusion Conditions:**
  1. The user has an authentic retrospective intent: they remember a past event, scene, visual element, or context that exists within their personal media library.
  2. The user experiences imperfect recall at retrieval onset: their mental representation lacks exact descriptors—such as an exact date (e.g., `2019-12-14`), an exact location (e.g., `Lat: 32.37, Long: 77.24`), an exact person/name, or exact textual metadata—and relies instead on approximate or experiential clues (e.g., remembering *"ice in Rohtang"* or *"five sisters"*). These descriptor categories serve as illustrative examples rather than fixed system requirements; the denominator is defined by the user's memory state, not current system capabilities.
  3. The user takes an observable retrieval action within the product to find that specific target.
- **Exclusion Conditions:**
  1. Users conducting generic exploratory browsing (e.g., casual timeline scrolling without a target).
  2. Users executing precise, unambiguous keyword lookups for which exact metadata is known (e.g., searching an exact album title, an exact contact tag, or an exact date like `"July 4, 2021"`).
  3. Users whose target photo does not exist in their library (unresolvable ground truth).

#### Numerator ($N_{\text{successful}}$): Successful Retrievals
- **Conceptual Definition:** The count of eligible users from the denominator who, within their initiated retrieval journey, surface the target candidate, recognize it as the item corresponding to their internal memory representation, and complete their retrieval intent.
- **Success Conditions:**
  1. The true target candidate is admitted into the displayed candidate pool.
  2. The user visually or contextually discriminates the target from distractors (Candidate Recognition).
  3. The user satisfies their retrieval task (e.g., explicit confirmation or terminal task action).

*Note: This definition establishes the conceptual population and success conditions. It does not invent numerical baselines or assume that a production telemetry schema already exists.*

---

## 2. Definition of "Imperfectly Remembered Photo"

The phrase *"a photo they remember but cannot precisely describe"* reflects the fundamental asymmetry between human episodic memory and database indexing. Grounded in the Part 1 memory-representation findings, an imperfect memory is neither a simple syntax error nor merely a "short query." 

Human memory retains vivid experiential facets while decaying along precise indexing dimensions. We define imperfect memory across four distinct memory states:

### A. Remembered Existence Without Searchable Metadata
The user possesses high certainty that the photograph exists in their library and recalls its personal significance, but cannot recall any structured database index fields:
- *Example:* The user remembers photographing a relative's official identity card during an administrative errand, but remembers neither the folder name, date, file format, nor exact text content.
- *Database Asymmetry:* The system indexes filenames, timestamps, and OCR tokens; the user's memory stores emotional necessity, an administrative episode, and a visual paper document.

### B. Salient Visual and Contextual Clues Without Exact Descriptors
The user retains vivid sensory or situational cues (colors, relative spatial configurations, concurrent actions, ambient lighting), but lacks standard categorical labels or formal object tags:
- *Example:* Remembering a yellow dog sitting on a kitchen rug, or festival lamps glowing at night.
- *Database Asymmetry:* The user remembers compositional co-occurrence (color bound to animal in a specific room); standard systems often index isolated bag-of-words tags (`dog`, `kitchen`, `yellow`) without relational binding.

### C. Approximate and Relative Context (Temporal, Spatial, Relational)
The user recalls entities, places, or timeframes only through subjective, relative, or colloquial anchors rather than absolute values:
- *Social Proxy:* Remembering *"5 sisters"* when the system only indexes unnamed faces or generic demographic counts.
- *Colloquial Dialect:* Remembering *"rohtang ki ice"* where the colloquial indicator `ki` connects a location to a visual state (`ice`), distinct from official administrative location tags.
- *Relative Temporal Milestones:* Remembering *"before covid"* or *"last winter trip"*, which require mapping relative historical epochs or seasonal anchors to Gregorian timestamp ranges.

### D. The Contrast: Precise Searchable Memory (Non-Target Population)
In contrast, a user with precise memory possesses the exact index keys: an exact contact name (`"Alice Smith"`), a calendar milestone (`"December 25, 2023"`), or a designated album title (`"Graduation 2022"`). 

The assignment's top-level metric is **strictly concerned with States A, B, and C**. Ordinary precise search (State D) bypasses the memory-discovery barrier and is excluded from the metric denominator.

---

## 3. Definition of "Start Searching"

To evaluate the top-level metric without biasing the product toward any specific UI implementation, the start of an eligible retrieval attempt must be defined **behaviorally and conceptually**, rather than tied to a single user interface widget.

### Behavioral Definition
A retrieval attempt begins at the timestamp where an eligible user **intentionally initiates an action within the application to locate a specific, internally remembered photo**.

### Interface-Agnostic Scope
This initiation boundary remains valid across current and future interaction paradigms:
- It does **not** assume a text search box.
- It does **not** assume a voice interface.
- It does **not** assume a conversational assistant or memory agent.
- It does **not** assume a filter chip or structured query builder.

### Conceptual Operationalization
An eligible retrieval attempt begins when:
1. **Deliberate Invocation:** The user transitions from passive feed consumption or app launch into active retrieval mode (e.g., submitting an open-ended retrieval expression, engaging a multi-modal query prompt, navigating to a discovery mechanism, or filtering by relative thematic cues).
2. **Episodic Intent:** The user's input expression or navigation behavior reflects an imperfect target representation (States A, B, or C described in Section 2).
3. **Session Boundary:** The retrieval attempt constitutes a bounded retrieval session—a sequence of contiguous discovery actions, query reformulations, or candidate inspections aimed at resolving the single underlying memory target.

---

## 4. Definition of "Successfully Retrieve"

A critical requirement of this business metric decomposition is that **system output must not be conflated with user success**. Surfacing data is a mechanical operation; retrieving a memory is a cognitive milestone.

### What Successful Retrieval Is NOT
- **Candidate Displayed $\neq$ Success:** Displaying a photo in a grid of 50 images is not success if the target is buried at rank 48, obscured by irrelevant distractors, or never inspected by the user.
- **Candidate Clicked $\neq$ Success:** A user click or tap on an image indicates curiosity, inspection, or false-positive investigation; it does not indicate that the clicked item is the actual remembered photo. A user frequently taps an image, realizes it is the wrong event, and immediately resumes searching.

### The Three-Stage Retrieval Progression
To define successful retrieval at the human-task level, we separate the retrieval lifecycle into three distinct, non-fungible stages:

```
[ Stage 1: Candidate Recovery ]
  The system admits the true target photo into the retrieved candidate set.
          ↓
[ Stage 2: Target Recognition ]
  The user visually/cognitively identifies the target as their intended memory.
          ↓
[ Stage 3: Task Completion ]
  The user confirms retrieval by concluding their search and acting on the photo.
```

#### 1. Candidate Recovery (Algorithmic Layer)
The retrieval engine successfully parses the imperfect query, bridges semantic and structural vocabulary gaps, and admits the true target photo into the candidate pool within an accessible ranking threshold ($R \le K$). If candidate recovery fails, downstream human success is impossible.

#### 2. Target Recognition (Cognitive Layer)
The user inspects the candidate pool and mentally matches the displayed visual evidence against their internal episodic memory. Recognition requires that:
- The candidate presentation preserves sufficient visual detail and context for the user to verify the memory.
- Competing distractors do not overwhelm or confuse the user's cognitive verification.

#### 3. Task Completion (Intent Fulfillment Layer)
The user resolves the original objective that motivated the search. Explicit user confirmation that the target was located represents the strongest conceptual success condition. In telemetry without direct explicit confirmation, behavioral interactions—such as sustained full-screen viewing without immediate return to search, or downstream actions like exporting, sharing, setting, editing, or adding the retrieved photo to a collection—are candidate observable signals that would require empirical validation rather than definitive proof of user recognition or successful retrieval. No validated behavioral threshold or fixed dwell-time duration is assumed.

Successful retrieval occurs **only when all three stages are satisfied**.

---

## 5. Causal Metric Decomposition

To decompose the top-level metric into measurable, actionable levers, we express human retrieval success as a product of conditional probabilities across the retrieval funnel.

### The Causal Chain

$$\text{Successful Retrieval Rate} = P(\text{Recovery} \mid \text{Eligible}) \times P(\text{Recognition} \mid \text{Recovery}, \text{Eligible}) \times P(\text{Completion} \mid \text{Recognition}, \text{Recovery}, \text{Eligible})$$

Where each component represents a strictly necessary sequential milestone:

```
Eligible Retrieval Attempt (Denominator, D_eligible)
  │
  ├─► [Condition 1: Candidate Recovery]
  │     Does the system admit the true target into the candidate pool?
  │     P(Candidate Recovery | Eligible)
  │
  ├─► [Condition 2: Candidate Recognition]
  │     Given recovery, does the user visually identify the target?
  │     P(Target Recognition | Recovery, Eligible)
  │
  └─► [Condition 3: Task Completion]
        Given recognition, does the user successfully conclude the task?
        P(Task Completion | Recognition, Recovery, Eligible)
```

### Component Definitions

1. **Eligibility ($D_{\text{eligible}}$):**
   Eligibility determines which retrieval attempts enter the denominator population ($D_{\text{eligible}}$); it is not itself a success-stage probability and is not multiplied into the top-level success rate.
   $$D_{\text{eligible}} = N_{\text{sessions}} \times P(\text{Imperfect Target Intent})$$

2. **Candidate Recovery Rate ($R_{\text{recov}}$):**
   The probability that, given an eligible retrieval attempt, the true target photo is recovered by the underlying retrieval engine within the visible candidate set ($K$):
   $$R_{\text{recov}} = P(\text{Target} \in \text{Candidates}_{\le K} \mid \text{Eligible})$$

3. **Candidate Recognition Rate ($R_{\text{recog}}$):**
   The probability that, given an eligible attempt and candidate recovery, the user discriminates and identifies the target as the remembered item:
   $$R_{\text{recog}} = P(\text{User Identifies Target} \mid \text{Recovery}, \text{Eligible})$$

4. **Task Completion Rate ($R_{\text{comp}}$):**
   The probability that, given candidate recovery and positive recognition, the user successfully concludes the retrieval session and fulfills their original goal:
   $$R_{\text{comp}} = P(\text{Task Fulfilled} \mid \text{Recognition}, \text{Recovery}, \text{Eligible})$$

### Unified Formulation
The top-level business metric is therefore formally decomposed as:

$$\mathbf{Successful\ Retrieval\ Rate} = R_{\text{recov}} \times R_{\text{recog}} \times R_{\text{comp}},\ \text{conditional on an eligible retrieval attempt.}$$

Eligibility determines which retrieval attempts enter the denominator; it is not itself a success-stage probability. This causal relationship demonstrates that an improvement in algorithmic candidate recovery ($R_{\text{recov}}$) is an **enabling condition**, but not an independent guarantee of overall business metric success.

---

## 6. Failure Modes of the Metric

Each stage of the causal decomposition presents unique failure conditions and distinct candidate observable signals:

| Metric Component | What Must Happen | Failure Condition | Candidate Observable Signals (Provisional — Require Empirical Validation) |
| :--- | :--- | :--- | :--- |
| **Eligibility** ($D_{\text{eligible}}$) | User has an authentic, imperfectly remembered target photo that exists in their library. | • Target does not exist in library (ground truth void).<br>• User is casually browsing without a target.<br>• User has exact metadata and executes precise lookup. | • Zero library ground truth.<br>• Rapid browsing of recent timeline with no query submission.<br>• Exact match on indexed name/album/date. |
| **Candidate Recovery** ($R_{\text{recov}}$) | Underlying engine admits true target into top-$K$ candidate pool. | • Zero-recall failure (0 candidates returned).<br>• Target excluded due to vocabulary/metadata mismatch.<br>• Target ranked below cutoff threshold ($R > K$). | • Empty result set returned.<br>• High semantic distance between query primitives and index tags.<br>• Multiple rapid query reformulations with zero candidate views. |
| **Candidate Recognition** ($R_{\text{recog}}$) | User visually identifies target among presented candidates. | • Target rendered outside active viewport.<br>• Target thumbnail too small/cropped to verify visual cues.<br>• Target obscured by visually identical distractors.<br>• Result set lacks event context or temporal clustering. | • User scrolls past candidate without interaction.<br>• Repeated inspection of distractor candidates followed by immediate bounce (candidate signal requiring validation).<br>• Extended dwell time on results page followed by abandonment (candidate signal requiring validation). |
| **Task Completion** ($R_{\text{comp}}$) | User confirms retrieval and satisfies their original intent. | • User identifies target but cannot open/view high-res photo.<br>• Retrieval process friction induces fatigue/abandonment before intended action.<br>• User doubts photo authenticity (e.g., similar photo from wrong year). | • Explicit user confirmation absent (strongest conceptual signal).<br>• Candidate opened but followed by session termination without terminal action (candidate signal requiring validation).<br>• Drop-off immediately following target inspection.<br>• Negative post-session user sentiment or feedback. |

*Note: Behavioral interactions (e.g., immediate bounce, extended dwell time, session termination without action) are candidate observable signals that would require empirical validation rather than definitive proof of user recognition or task completion. Explicit user confirmation remains the strongest conceptual success condition; no validated behavioral threshold or fixed dwell-time duration is assumed.*

---

## 7. Connecting Part 1 Findings to Part 2 Metric Decomposition

### Scope Clarification: What Part 1 Did and Did Not Measure
It is vital to maintain strict methodological discipline regarding the Part 1 experiment:

> **CRITICAL DISTINCTION:**
> **Part 1 was NOT a user-level experiment.** Part 1 did not measure human users, human recognition, human fatigue, or end-to-end task completion.
> 
> Therefore, **Part 1 did NOT measure the top-level business metric.**
> 
> **Part 1 primarily and specifically tested the Candidate Recovery component ($R_{\text{recov}}$)** within an audited, controlled offline benchmark of 65 candidate records.

### Mapping Part 1 Experimental Cases to Candidate Recovery Mechanisms

The controlled cases evaluated in Part 1 demonstrate specific architectural mechanisms required to satisfy the **Candidate Recovery** condition ($R_{\text{recov}}$):

| Part 1 Case | Query Formulation | Underlying Recovery Mechanism Tested | Contribution to Candidate Recovery ($R_{\text{recov}}$) |
| :---: | :--- | :--- | :--- |
| **Case 1** | `"5 sisters"` | **Candidate recovery through demographic proxy** | Translates unindexed social kinship roles into visible demographic primitives (`count: 5`, `gender: female`), recovering targets missed entirely by literal search (Recall: $0.0 \rightarrow 1.0$). |
| **Case 2** | `"rohtang ki ice wali photo"` | **Candidate discrimination & noise suppression** | Strips colloquial particles (`ki`, `wali`), extracts geographic entity (`Rohtang`) and visual modifier (`ice`), ranking the true mountain target over competing indoor ice-cream distractors. |
| **Case 3** | `"yellow dog in kitchen"` | **Compositional entity-attribute candidate evaluation** | Evaluates spatial and visual binding between entity (`dog`), color modifier (`yellow`), and scene (`kitchen`), eliminating false positives that contain uncoordinated keywords. |
| **Case 4** | `"diwali lights at night"` | **Multi-path retrieval parity preservation** | Confirms that multi-path semantic discovery preserves high recall and ranking when standard literal indexing already succeeds (Baseline Recall: 1.0; Discovery Engine Recall: 1.0). |
| **Case 5** | `"doc with aadhar number"` | **Literal in-image text candidate recovery** | Recovers text-bearing documents by pairing OCR extraction with literal pattern anchors, bridging the gap between natural concept ("aadhar") and indexed OCR text. |
| **Case 6** | `"shimla snowfall before covid"` | **Approximate temporal candidate evaluation** | Resolves relative historical epochs (`"before covid"` $\rightarrow$ pre-March 2020) and seasonal snow patterns to bound candidate retrieval temporally without exact dates. |
| **Case 7** | `"photos of aarav"` | **Candidate coverage across multi-day sessions** | Overcomes session truncation to recover candidates spanning disparate dates (10 of 10 days recovered vs. 2 of 10 for baseline), preventing false zero-recall across time. |
| **Case 8** | `"manali trip 2022"` | **Candidate organization & event clustering** | Clusters temporal and geographic candidates into coherent episodic event structures, preparing candidate sets for structured visual consumption. |

### Summary of Connection
Part 1 demonstrated that structured memory representation and multi-path discovery can improve candidate recovery for imperfect descriptions under the controlled benchmark conditions (+35% Target Recall, +37.5% P@1). However, because the top-level business metric is a multiplicative function of Recovery, Recognition, and Completion, Part 1 validates only the technical recovery layer—it did not measure user recognition, task completion, end-to-end successful retrieval, or business impact, and does not demonstrate user-level success.

---

## 8. Leading vs. Lagging Metrics

To track progress toward the strategic goal without conflating causes and effects, we classify metrics logically implied by the decomposition into leading indicators and lagging outcomes.

```
       LEADING INDICATORS                     LAGGING OUTCOME
┌───────────────────────────────┐      ┌──────────────────────────────┐
│  • Candidate Recovery Rate    │      │                              │
│  • Candidate Coverage@K       │ ───► │   Successful Retrieval Rate  │
│  • Precision@K in Visible Pool│      │   for Imperfect Memories     │
│  • Recognition Opportunity    │      │                              │
└───────────────────────────────┘      └──────────────────────────────┘
```

### Lagging Outcome Metric
- **Metric:** **Successful Retrieval Rate for Imperfectly Remembered Photos ($N_{\text{successful}} / D_{\text{eligible}}$)**
- **Role:** The true business and user outcome. It measures whether users actually solve their retrieval problems.
- **Why It Lags:** It can only be evaluated after full retrieval sessions conclude, requiring end-to-end user interaction, cognitive evaluation, and intent resolution.

### Leading Indicator Metrics
Leading indicators measure intermediate system and behavioral states that causally enable the lagging outcome. A metric is a leading indicator **only if an improvement in that metric directly increases the probability of downstream success**:

1. **Target Candidate Recovery Rate ($R_{\text{recov}}$):**
   - *Causal Link:* If the target photo is not in the candidate pool, recognition and completion probability is strictly zero ($P = 0$). Increasing candidate recovery directly expands the opportunity for success.
2. **Candidate Coverage in Visible Viewport (Coverage@K):**
   - *Causal Link:* Users rarely scroll through hundreds of candidates. The percentage of eligible queries where the true target is retrieved within the top visual viewport (e.g., $K \le 10$) directly drives downstream recognition.
3. **Candidate Pool Precision (Distractor Ratio):**
   - *Causal Link:* High distractor density increases visual fatigue and causes recognition failure. Elevating precision within the candidate pool reduces cognitive search cost.
4. **Recognition Opportunity Rate:**
   - *Causal Link:* The proportion of sessions where a recovered target is successfully rendered within the active user viewport under conditions permitting visual inspection. (Exposure duration and viewport dwell are candidate observable signals that would require empirical validation rather than an assumed fixed dwell-time threshold.)

---

## 9. Metric Tree

The following metric tree represents the full causal and diagnostic structure of the business metric. It shows the primary decomposition into user milestones, alongside underlying diagnostic mechanisms.

```
TOP-LEVEL BUSINESS OUTCOME:
Successful Retrieval Rate for Imperfectly Remembered Photos
[ N_successful / D_eligible ]
  │
  ├── 1. ELIGIBLE RETRIEVAL ATTEMPTS (Denominator, D_eligible)
  │     ├── Authentic Retrospective Intent (Target exists in user library)
  │     └── Imperfect Memory State (Lacks exact indexable descriptors: States A, B, C)
  │
  ├── 2. TARGET CANDIDATE RECOVERY (Algorithmic Layer, R_recov)
  │     ├── Target Recall (Target admitted into candidate pool)
  │     ├── Target Rank Position (Target within visible threshold K)
  │     │
  │     └── [Diagnostic Mechanisms — Not Separate Business KPIs]
  │           ├── Representation Alignment (Bridging human concept to metadata primitive)
  │           ├── Multi-Path Generation (Demographic, OCR, Visual, Temporal coverage)
  │           ├── Compositional Binding (Pairing attributes to correct entities)
  │           ├── Colloquial/Noise Stripping (Suppressing non-indexing particles)
  │           └── Session Boundary Preservation (Multi-day coverage vs. truncation)
  │
  ├── 3. TARGET CANDIDATE RECOGNITION (Cognitive Layer, R_recog)
  │     ├── Viewport Visibility (Target presented in user's active visual field)
  │     ├── Visual Clue Preservation (Resolution/thumbnail sufficient to verify memory)
  │     ├── Distractor Discrimination (True target discriminable from visual peers)
  │     └── Event Context Coherence (Clustered episodic grouping aids memory anchoring)
  │
  └── 4. TASK COMPLETION (Intent Fulfillment Layer, R_comp)
        ├── Session Resolution (Search terminates without reformulation/bounce)
        ├── Photo Inspection/Verification (Full-screen view or high-res confirmation)
        └── Terminal Value Realization (Share, export, use, or confirm memory)
```

> **IMPORTANT ARCHITECTURAL GOVERNANCE:**
> The diagnostic branches under Target Recovery (e.g., representation alignment, compositional binding, multi-path coverage) are **technical diagnostic mechanisms**, not independent business outcomes. They explain *why* recovery succeeds or fails; they must never be substituted for the top-level user outcome.

---

## 10. What We Should NOT Measure Yet

When decomposing search initiatives, teams are often tempted to reach for standard consumer search and engagement metrics. In the context of imperfect memory retrieval, these metrics are **premature, deceptive, or directly off-anchor**:

| Tempting Metric | Why It Is Dangerous / Off-Anchor at This Stage |
| :--- | :--- |
| **Daily Active Users (DAU) / MAU** | DAU reflects macro acquisition, notification triggers, and habits; it does not measure whether a user with an imperfect memory retrieved their photo. |
| **Search Frequency / Queries per User** | Ambiguous valence. High query frequency often indicates **search failure** (a frustrated user repeatedly reformulating queries because the engine cannot find their photo). |
| **Generic Search Click-Through Rate (CTR)** | Clicking a photo does not equate to finding the target. Users frequently click distractors out of curiosity or mistaken identity, only to resume searching immediately. |
| **Result Clicks Count** | High click volume often signals high candidate ambiguity, where the user must inspect multiple incorrect photos before finding (or abandoning) the target. |
| **Time Spent in Search / Session Duration** | Ambiguous valence. Long session duration can signify either deep engagement or severe retrieval friction and cognitive exhaustion. |
| **Generic Search Latency (P50/P99)** | While latency is a relevant system constraint, optimizing for sub-millisecond retrieval of the *wrong* candidates does nothing to solve imperfect memory retrieval. |
| **Feature Adoption / Mode Usage (e.g., Voice, Assistant)** | Measures user curiosity toward a specific UI mechanism rather than whether the user's underlying retrieval task was resolved. |

These metrics may serve as secondary guardrails or operational telemetry later in the product lifecycle, but **none of them answer the assignment's strategic question**.

---

## 11. Current Measurement Gaps

To maintain strict scientific integrity, we explicitly document what this project currently **does not have evidence to measure**:

1. **Real-World Denominator Size ($D_{\text{eligible}}$):**
   We currently have no empirical telemetry measuring how often real Google Photos users experience an imperfect memory retrieval need versus precise search or passive browsing.
2. **User-Level Successful Retrieval Rate ($N_{\text{successful}} / D_{\text{eligible}}$):**
   Because Part 1 was an offline synthetic benchmark, we have zero empirical data measuring actual human task completion on imperfect retrieval tasks.
3. **Cognitive Recognition Success Rate ($R_{\text{recog}}$):**
   We have no measured data on whether real users, when presented with recovered candidates alongside realistic library distractors, can successfully discriminate and recognize their target.
4. **Task Completion and Terminal Intent ($R_{\text{comp}}$):**
   We have no data on downstream user behavior following candidate inspection (e.g., share rates, abandonment rates, confirmation rates).
5. **Candidate Recovery in Production-Scale Personal Libraries:**
   Part 1 evaluated 65 candidate records across 8 structured test cases. We do not have measurements of Candidate Recovery ($R_{\text{recov}}$) in uncurated libraries containing tens of thousands of real, noisy, unsegmented photos.
6. **The Empirical Transfer Function Between Candidate Recovery and User Success:**
   We do not know the exact mathematical elasticity between an algorithmic recall improvement (e.g., +35% recall) and the resulting change in user-perceived task completion.

These gaps establish why **future user-facing validation and empirical research are strictly necessary** before claiming business impact.

---

## 12. Conclusion

The assignment's strategic goal:

$$\text{"Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching"}$$

is a **human-task outcome metric**, not a system performance benchmark.

### Core Takeaways of the Decomposition:
1. **The Metric Is Bounded by Cognition:** The retrieval journey begins with an authentic, imperfect episodic memory (States A, B, or C) and succeeds only when the user reaches task completion through verification.
2. **The Causal Chain Is Multiplicative:** 
   $$\text{Successful Retrieval Rate} = \text{Recovery} \times \text{Recognition} \times \text{Completion},\ \text{conditional on an eligible retrieval attempt.}$$
   Eligibility determines which retrieval attempts enter the denominator; it is not itself a success-stage probability. A complete failure at any single downstream stage causes total retrieval failure.
3. **Part 1 Established the Recovery Foundation:** The Part 1 proof-of-concept benchmark demonstrated that structured memory representation and multi-path discovery can improve candidate recovery for imperfect descriptions under the controlled benchmark conditions (+35% Target Recall).
4. **The Critical Next Boundary:** Part 1 demonstrated that structured memory representation and multi-path discovery can improve candidate recovery for imperfect descriptions under the controlled benchmark conditions. However, Part 1 did not measure user recognition, task completion, end-to-end successful retrieval, or business impact. The remaining stages—**Candidate Recognition ($R_{\text{recog}}$)** and **Task Completion ($R_{\text{comp}}$)**—remain unvalidated.

Subsequent project phases must focus on testing whether bridging this recovery gap actually enables human users to recognize and retrieve their memories in real-world environments, without prematurely prescribing UI designs, features, or product solutions.
