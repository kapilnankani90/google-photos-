# Part 1 — Experimental Findings

## 1. What the Experiment Tested

The primary architectural question of Part 1 evaluates whether a structured Discovery Engine can transform imperfect, natural human memory descriptions into multi-modal retrieval representations that recover and organize photo candidates more effectively than literal keyword lookup:

$$\mathbf{PROJECT\ ANCHOR:}\ \text{Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching.}$$

To test this question without premature production assumptions, a controlled proof-of-concept experiment was executed comparing two deterministic retrieval strategies:
- **Strategy A (Direct / Literal Baseline):** Direct keyword tokenization and literal matching against candidate metadata fields, with zero semantic expansion, zero entity-attribute binding, zero colloquial particle stripping, and zero temporal window calculation.
- **Strategy B (Discovery Engine Pipeline):** End-to-end execution of the locked seven-stage conceptual architecture: Memory Interpretation $\rightarrow$ Retrieval Signal Generation $\rightarrow$ Multi-Path Discovery $\rightarrow$ Candidate Coverage Checking $\rightarrow$ Controlled Recovery $\rightarrow$ Compositional Matching $\rightarrow$ Result Organization.

The test suite evaluated both strategies against a fixed, audited benchmark corpus ([part1_experimental_benchmark.json](file:///d:/graduation%20project%203/part1_experimental_benchmark.json)) containing **65 structured candidate records** across 8 empirical cases derived directly from project user interviews and public research evidence.

---

## 2. Overall Experimental Result

The aggregate performance across all eight experimental retrieval cases is summarized below:

| Metric | Direct / Literal Baseline | Discovery Engine | Observed Difference |
| :--- | :---: | :---: | :---: |
| **Mean Target Recall** | 0.650 (65.0%) | 1.000 (100.0%) | **+0.350 (+35.0%)** |
| **Mean Tie-Adjusted Precision@1** | 0.406 (40.6%) | 0.781 (78.1%) | **+0.375 (+37.5%)** |
| **Zero-Result Failure Cases** | 2 of 8 cases (25.0%) | 0 of 8 cases (0.0%) | **-2 cases (-25.0%)** |
| **Case 7 Multi-Session Coverage** | 2 of 10 days (20.0%) | 10 of 10 days (100.0%) | **+8 days ($5.0\times$ expansion)** |
| **False Positives Admitted** | 19 non-targets | 15 non-targets | **-4 non-targets** |

### Factual Interpretation of Overall Results
Within this controlled benchmark, the observed differences demonstrate that structured memory representation and multi-modal signal generation alter retrieval behavior across three primary dimensions:
1. **Recall Recovery:** Admitting target candidates into the retrieval pool when the user's remembered vocabulary does not literally exist in index metadata (e.g., social kinship roles and in-image text).
2. **Candidate Discrimination:** Elevating true targets over competing noise by binding modifiers directly to host entities rather than treating attributes as uncoordinated bag-of-words keywords.
3. **Recall Preservation & Organization:** Detecting session-level truncation to recover recurring entities across time, and clustering multi-day milestones into coherent event structures.

These findings validate the internal logic of the conceptual architecture. They do not demonstrate that photo search is "solved," nor do they prove production-scale performance across uncurated libraries.

---

## 3. Finding 1 — Memory Representation Can Recover Candidates Literal Retrieval Misses

### Empirical Case: Case 1 (`"5 sisters"`)

#### Experimental Observation
- **Direct Baseline (Strategy A):** Target Recall = **0.000** (0/1 targets recovered). Rank 1 was assigned to `c1_dist_literal_sister_sign` (a commercial bakery storefront containing the printed text `"Seven Sisters Bakery"`, Score: 0.50). The family target received a score of 0.000.
- **Discovery Engine (Strategy B):** Target Recall = **1.000** (1/1 targets recovered). The family target (`c1_tgt_family_5sisters`) achieved Rank 1 (Score: 2.00).

#### Architectural Mechanism
The user remembers a social kinship relationship (`sister`) and an explicit count (`5`). Personal photo libraries index visual entities and demographic primitives, not private genealogical trees. Strategy B ingests `"5 sisters"` into a structured frame (`people: [{role: "sister", count: 5}]`) and derives demographic retrieval signals: `[group_count: 5, apparent_gender: female]`. This demographic proxy queries candidate portraits matching the group size and gender primitives, successfully recovering the unindexed family photograph.

#### What It Demonstrates
Some remembered human concepts cannot be matched directly against literal metadata. Transforming natural social memory into intermediate demographic search primitives enables the admission of valid candidates that literal string matching completely misses.

#### Critical Limitation
Demographic translation recovers groups of five females, but it cannot biologically verify sisterhood. In the experiment, `c1_rel_campus_5females` (a college reunion of five female friends) also scored 2.00 and tied with the target at Rank 1. The experiment demonstrates **candidate recovery via demographic proxy**, not relationship verification. True disambiguation requires surrounding event context or user recognition.

---

## 4. Finding 2 — Structured Decomposition Can Improve Retrieval When Recall Already Exists

### Empirical Case: Case 2 (`"rohtang ki ice wali photo"`)

#### Experimental Observation
- **Direct Baseline (Strategy A):** Target Recall = **1.000** (1/1 targets recovered). However, the target (`c2_tgt_rohtang_snow`, Score: 0.40) was tied with three distractors at Rank 1, including `c2_dist_wali_sign` ("Paranthe Wali Gali Famous Photo Studio", Score: 0.40) and `c2_dist_solang_snow` (Score: 0.40). Tie-adjusted Precision@1 was **0.250**.
- **Discovery Engine (Strategy B):** Target Recall = **1.000**. The target uniquely held Rank 1 with a score of **2.000**. Tie-adjusted Precision@1 improved to **1.000**.

#### Architectural Mechanism
The user expressed memory using code-mixed Hinglish syntax containing communicative postpositions (`ki`, `wali`, `photo`). Strategy A treated all five words as literal query keywords, allowing `c2_dist_wali_sign` to match `"wali"` and `"photo"`. Strategy B decomposed the expression, stripping grammatical particles while preserving `raw_input`, and isolated the geographic landmark (`spatial: "rohtang"`) and physical visual element (`objects: ["ice"]`).

#### What It Demonstrates
Better memory representation improves candidate discrimination and ranking even when literal retrieval already has access to the target. Isolating vernacular syntax prevents conversational filler words from acting as accidental query keywords that elevate irrelevant distractors.

#### Methodological Clarification
This case is **not** a zero-result recovery case in the benchmark (since the baseline recovered the target with partial token matches). It is an experimental demonstration of **candidate disambiguation and ranking elevation** via particle stripping and spatial-object decomposition.

---

## 5. Finding 3 — Entity-Attribute Binding Changes Candidate Meaning

### Empirical Case: Case 3 (`"white bike"`)

#### Experimental Observation
- **Direct Baseline (Strategy A):** Target Recall = **1.000**. However, the target was tied at Rank 1 with three competing candidates, including `c3_dist_black_bike_white_shirt` (black motorcycle with a rider in a white shirt, Score: 1.00) and `c3_dist_black_bike_white_wall` (black motorcycle parked against a white wall, Score: 1.00). Tie-adjusted Precision@1 was **0.250**.
- **Discovery Engine (Strategy B):** Target Recall = **1.000**. The white motorcycle (`c3_tgt_white_motorcycle`) held Rank 1 uniquely (Score: **2.000**). Disconnected attribute distractors were demoted to Rank 3 (Score: **1.000**). Tie-adjusted Precision@1 improved to **1.000**.

#### Architectural Mechanism
Strategy A evaluated `"white"` and `"bike"` as uncoordinated bag-of-words tokens, awarding full credit whenever both words appeared anywhere in candidate tags. Strategy B evaluated the attribute directly on its host entity (`objects.bike.attribute_white`). For the true target, the motorcycle body was white (`bound_attribute = 1.00`). For the distractors, the white color was bound to `clothing` or `wall`, resulting in `bound_attribute = 0.00`.

#### What It Demonstrates
Retrieval clues cannot be evaluated as independent tokens when human memory specifies an attribute bound to an entity. Preserving entity-attribute binding fundamentally changes candidate interpretation, preventing false-positive flooding from disconnected background or clothing colors. This represents one of the clearest empirical validations of the architecture's compositional matching layer.

---

## 6. Finding 4 — Multi-Path Retrieval Can Provide Alternative Access Paths

### Empirical Case: Case 4 (`"diya at the gate"`)

#### Experimental Observation
- **Direct Baseline (Strategy A):** Target Recall = **1.000**; Tie-adjusted Precision@1 = **1.000** (Score: 0.75, Rank 1).
- **Discovery Engine (Strategy B):** Target Recall = **1.000**; Tie-adjusted Precision@1 = **1.000** (Score: 2.00, Rank 1).

#### Architectural Mechanism
The memory specifies a salient object (`diya`) co-occurring at a spatial architectural boundary (`gate`) with an unindexed acquaintance (residential watchman). Strategy B activated visual entity and spatial environmental discovery paths independently, scoring the intersection compositionally without requiring facial recognition tags.

#### What It Demonstrates & Preserved Limitation
In this synthetic benchmark, candidate metadata explicitly contained both `"diya"` and `"residential entrance gate"`. Consequently, Strategy A's direct keyword search was also capable of retrieving the target at Rank 1.

**We do NOT claim that the Discovery Engine outperformed keyword search in this case.** 

The empirical value of Case 4 is that it confirms the architecture can successfully represent and retrieve a multi-clue memory through independent object and spatial paths. In real-world evidence (Interview Episode 25), users initially experienced failure because they attempted person-centric search for an unindexed contact. The experiment demonstrates that multi-path retrieval provides an alternative access path independent of biometric clustering, but it does **not** demonstrate a baseline failure when literal metadata tags are fully present.

---

## 7. Finding 5 — Dedicated Literal-Text Routing Can Recover In-Image Text

### Empirical Case: Case 5 (`"Progressive"`)

#### Experimental Observation
- **Direct Baseline (Strategy A):** Target Recall = **0.000** (0/1 targets recovered). Standard image metadata tags did not contain the commercial brand name. All candidates scored 0.000.
- **Discovery Engine (Strategy B):** Target Recall = **1.000** (1/1 targets recovered). The auto insurance policy document (`c5_tgt_progressive_insurance_policy`) achieved Rank 1 (Score: 1.00).

#### Architectural Mechanism
Strategy B interpreted the single-token brand name as literal in-image text (`literal_text: ["Progressive"]`), routing it directly to the OCR text retrieval path rather than treating it as a descriptive adjective or conversational prompt.

#### Methodological Boundary & Exact Claim
In the live public evidence (Reddit Case 5), an interactive conversational LLM treated `"Progressive"` as an abstract conversational query and responded with a chatbot refusal (*"I can't help with that"*). 

The controlled benchmark does **not** reproduce a live conversational LLM dialog refusal. Instead, it models the structural retrieval consequence: querying standard image tags yields zero results because printed text is embedded within the image. 

Therefore:
$$\mathbf{EXACT\ CLAIM:}\ \text{The controlled experiment demonstrates the value of an explicit in-image text retrieval path}$$
$$\text{under the benchmark's modeled failure condition. It does not claim to directly measure production Google Photos behavior.}$$

---

## 8. Finding 6 — Approximate Temporal Memory Can Be Represented Without an Exact Date

### Empirical Case: Case 6 (`"document around 4 years ago"`)

#### Experimental Observation
- **Direct Baseline (Strategy A):** Target Recall = **1.000**. However, the target (`c6_tgt_lease_agreement_2022`, Score: 0.40) was demoted to Rank 2 behind an 8-year-old tax form (`c6_dist_old_document_2018`, Score: 0.60) which matched accidental token fragments. Tie-adjusted Precision@1 was **0.000**.
- **Discovery Engine (Strategy B):** Target Recall = **1.000**. The target achieved Rank 1 (Score: **2.000**). Tie-adjusted Precision@1 was **0.500** (tied with a relevant bank statement from the same era; non-era documents were demoted).

#### Architectural Mechanism
The user recalled an object type (`document`) and a coarse, hedged relative timeframe (`around 4 years ago`). Strategy A cannot evaluate relative linguistic hedging against ISO timestamps. Strategy B mapped `"around 4 years ago"` into a continuous historical interval $[t - 4.5\text{y}, t - 3.5\text{y}]$ relative to reference time $t = \text{2026-09-30}$. Candidates within this continuous window received full temporal congruence (`temporal = 1.00`), while documents from 2026 (0.56y ago) and 2018 (8.47y ago) received `temporal = 0.00`.

#### What It Demonstrates
Human temporal memory does not need to be converted into an exact calendar date (`YYYY-MM-DD`) before search can occur. Continuous interval scoring enables systems to evaluate approximate temporal memories directly against timestamp metadata, demoting out-of-era documents without rejecting conversational hedging.

---

## 9. Finding 7 — Candidate Coverage Checking Can Expand Retrieval Across Sessions

### Empirical Case: Case 7 (`"yellow truck"`)

#### Experimental Observation
- **Direct Baseline (Strategy A):** Target Recall = **0.200** (only 2 of 10 target days captured due to simulated single-session presentation truncation).
- **Discovery Engine (Strategy B):** Target Recall = **1.000** (10 of 10 target days recovered).
- **Coverage Expansion:** **$5.0\times$ increase** in temporal entity coverage.

#### The Controlled Sequence Executed
```
PHASE 1 (Initial Probe):
  └─ Initial pool captured only Day 1 and Day 2 (c7_tgt_truck_day01, c7_tgt_truck_day02).
PHASE 2 (Candidate Coverage Check):
  └─ Evaluated: "Does candidate set capture the recurring temporal span of query entity?"
  └─ Diagnosis: INSUFFICIENT ("Candidate set is temporally concentrated in only 2 initial sessions...")
PHASE 3 (Controlled Recovery):
  └─ Action: Broadened search along June 2024 project timeline.
  └─ Recovered: 8 additional distinct target days (Day 3 through Day 10).
PHASE 4 (Final Evaluation):
  └─ All 10 distinct days achieved Score 2.00 (truck: 1.0, yellow: 1.0) and tied at Rank 1.
```

#### Why This Differs from Ordinary Ranking
The architecture does not merely re-rank candidates that were already gathered. It introduces a structural **Coverage Check** that inspects the candidate pool *before* final evaluation to determine whether retrieval is premature or incomplete. When a recurring entity exhibits an artificial temporal gap, it triggers controlled broadening to protect recall.

#### Critical Limitation
This experiment is a controlled simulation of candidate truncation and temporal broadening based on Reddit Case 11. It demonstrates the conceptual validity of a coverage check mechanism; it does **not** prove automated recurring-object tracking across production-scale media libraries.

---

## 10. Finding 8 — Result Organization Can Add Value Even When Retrieval Recall Is Identical

### Empirical Case: Case 8 (`"wedding"`)

#### Experimental Observation
- **Direct Baseline (Strategy A):** Target Recall = **1.000** (3/3 wedding target photos recovered); Tie-adjusted Precision@1 = **0.750**.
- **Discovery Engine (Strategy B):** Target Recall = **1.000** (3/3 wedding target photos recovered); Tie-adjusted Precision@1 = **0.750**.

#### The Architectural Difference: Stage 6 Result Organization
Because both strategies recovered wedding photos and scored them identically (`1.00`), the architectural finding is **not** superior retrieval recall or scoring. The value appears entirely in **Stage 6 (Result Organization)**:
- **Baseline Behavior:** Presents individual wedding photos scattered across uncalibrated rows, disconnecting ceremony moments from reception moments (simulating the disorientation documented in Reddit Case 10).
- **Discovery Engine Behavior:** Clusters candidates into structured event episodes with chronological landmarks:
  - **Cluster 1: Meera Wedding (Target Event Cluster):** Sangeet Night (Nov 17) $\rightarrow$ Main Ceremony (Nov 18) $\rightarrow$ Grand Reception (Nov 19).
  - **Cluster 2: Rohan Colleague Wedding (Secondary Cluster):** Colleague wedding from 2021 segregated into its own timeline.
  - **Cluster 3: Non-Wedding Celebrations (Excluded):** Birthday parties, corporate galas, and festival dinners filtered or placed in non-wedding categories.

#### What It Demonstrates
For broad milestone memories, user retrieval success depends on visual context and event structure. Organizing candidates into multi-day chronological episodes allows users to recognize surrounding moments, providing usability value that relevance ranking alone cannot deliver.

---

## 11. Cross-Case Synthesis

The table below synthesizes the eight empirical cases into their core architectural mechanisms:

| Memory Characteristic | Architectural Mechanism Tested | Primary Evidence Case | Observed Retrieval Effect | Key Strength & Empirical Boundary |
| :--- | :--- | :--- | :--- | :--- |
| **Relational Kinship Memory** | Relational translation to demographic primitives | Case 1 (`"5 sisters"`) | Recovers target from 0% to 100% recall | Recovers candidate portraits, but cannot verify biological sisterhood. |
| **Code-Mixed Vernacular Syntax** | Conversational particle stripping | Case 2 (`"rohtang ice wali"`) | Eliminates keyword ties with distractor signs; P@1 0.25 $\rightarrow$ 1.00 | Improves ranking discrimination; target was partially retrievable in baseline. |
| **Compositional Entity + Attribute** | Entity-attribute binding | Case 3 (`"white bike"`) | Demotes disconnected color matches; P@1 0.25 $\rightarrow$ 1.00 | Clearly isolates bound attributes; relies on entity detection backends. |
| **Spatial / Object Co-occurrence** | Multi-path environmental retrieval | Case 4 (`"diya gate"`) | Recovers candidate without face recognition | Target was also retrievable by keyword baseline when tags existed. |
| **In-Image Literal Text** | Dedicated OCR in-image text routing | Case 5 (`"Progressive"`) | Recovers document from 0% to 100% recall | Tests metadata lookup failure; does not reproduce live LLM refusal. |
| **Approximate Relative Time** | Continuous temporal windowing | Case 6 (`"4 years ago"`) | Elevates era documents over out-of-era forms; P@1 0.00 $\rightarrow$ 0.50 | Eliminates rigid calendar date requirement; retains era document ambiguity. |
| **Recurring Multi-Session Entity** | Candidate coverage check & recovery | Case 7 (`"yellow truck"`) | Expands multi-day recall from 20% to 100% ($5.0\times$ expansion) | Demonstrates recovery logic; tested under controlled truncation simulation. |
| **Broad Milestone Event** | Event clustering & landmark sequencing | Case 8 (`"wedding"`) | Structures multi-day event coherence | Retrieval recall is identical; value is in contextual organization. |

---

## 12. What the Experiment Supports

Within the strict limits of this proof-of-concept, the empirical results support the following foundational claim:

$$\mathbf{SUPPORTED\ ARCHITECTURAL\ CLAIM:}$$
$$\text{"The controlled experiment supports the architectural hypothesis that richer structured memory representations}$$
$$\text{and multi-path retrieval signals can recover, discriminate, expand, and organize candidates differently}$$
$$\text{from direct literal interpretation across several controlled retrieval scenarios."}$$

Specifically, the experiment provides verified evidence that:
1. Transforming non-indexed relationships into visual search primitives recovers candidates that direct keyword search drops.
2. Evaluating attributes directly on host entities prevents false-positive ranking flooding.
3. Decoupling candidate discovery from ranking and introducing a coverage check protects recall against premature session truncation.
4. Structuring broad results by event landmarks preserves multi-day context without requiring manual chronological scrolling.

---

## 13. What the Experiment Does NOT Establish

Scientific integrity requires explicitly stating what this experiment did **not** prove:

1. **Does not establish production Google Photos performance:** The experiment ran against 65 synthetic JSON records, not Google's proprietary petabyte-scale infrastructure.
2. **Does not establish user-level retrieval success:** Success on benchmark records indicates algorithmic validity, not real-world user retrieval rates.
3. **Does not establish user satisfaction or completion time:** No human interaction, UI usability, or cognitive search fatigue was measured.
4. **Does not test large photo libraries:** Real users possess 50,000+ uncurated, blurry, duplicate, and mislabeled images; scalability across large indexes remains unmeasured.
5. **Does not evaluate real LLM or vision backends:** Interpretation and candidate tags were deterministic representations, not live machine learning models.
6. **Does not prove all fuzzy memories benefit from structure:** Simple queries (e.g., `"dog"`, `"beach"`) are already served well by literal search; structured decomposition introduces unnecessary overhead for direct memories.
7. **Case 1 retains demographic ambiguity:** Demographic translation recovers female groups of five, but cannot confirm kinship.
8. **Case 4 does not demonstrate a baseline failure:** Strategy A also succeeded when metadata contained both terms.
9. **Case 5 models metadata lookup failure rather than reproducing live conversational refusal:** Chatbot prompt refusal was modeled through retrieval routing consequences.
10. **Case 7 is a controlled simulation:** The 2-day truncation was an experimental simulation, not an observed production database crash.
11. **Case 8 demonstrates organizational structuring, not ranking superiority:** Relevance scores were identical between strategies.

---

## 14. Part 1 Conclusion

$$\mathbf{PART\ 1\ SYNTHESIS:}\ \text{What did we learn from the Discovery Engine experiment?}$$

The controlled experiment demonstrated that the primary reason users fail to retrieve remembered photos is an **impedance mismatch** between how humans remember events (relational roles, approximate time, bound attributes, vernacular phrasing, recurring episodes) and how search engines index images (literal keyword tags, exact calendar dates, uncoordinated bag-of-words labels, rigid presentation caps).

By inserting a structured interpretation layer and generating multi-path retrieval signals, the Discovery Engine successfully bridged this representational gap across every test case in our controlled benchmark.

Part 1 has completed its mandate: it has established an experimentally verified architectural direction grounded in empirical failure evidence. 

The next stage of the project can use these architectural learnings to investigate how the retrieval concept should be validated with actual users and eventually translated into an AI-native product experience.
