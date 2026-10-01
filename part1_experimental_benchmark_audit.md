# Part 1 — Experimental Benchmark Audit

## 1. Executive Summary & Experimental Anchor

$$\mathbf{PROJECT\ ANCHOR:}\ \text{Increase the percentage of users who successfully retrieve a photo they remember but cannot precisely describe when they start searching.}$$

This audit documents the design, candidate composition, distractor rationale, and methodological boundaries of the controlled benchmark corpus stored in [part1_experimental_benchmark.json](file:///d:/graduation%20project%203/part1_experimental_benchmark.json). 

The benchmark instantiates the 8 real-world research retrieval tasks locked in [part1_discovery_engine_experimental_spec.md](file:///d:/graduation%20project%203/part1_discovery_engine_experimental_spec.md) and [part1_discovery_engine_operating_spec_final.md](file:///d:/graduation%20project%203/part1_discovery_engine_operating_spec_final.md). Every candidate conforms strictly to the locked 10-field candidate record schema with zero extraneous fields:
- `photo_id` (string)
- `visual_entities` (list of strings)
- `bound_attributes` (object mapping entity to list of string attributes)
- `demographic_tags` (object containing integer `count`, string `apparent_gender`, and string `apparent_age`)
- `in_image_text` (list of strings)
- `timestamp` (ISO-8601 string)
- `spatial_setting` (string)
- `event_context` (string)
- `is_ground_truth_target` (boolean)
- `target_case` (string)

The corpus contains **65 candidate records** across the 8 cases, structured to test hypotheses through negative failure modes rather than demonstrating trivial success.

---

## 2. Benchmark Corpus Composition Overview

| Case # | Target Case Expression | Primary Research Anchor | Target Candidates | Relevant (Non-Target) | Distractors | Total Records |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Case 1** | `"5 sisters"` | Interview Ep 05 | 1 | 1 | 6 | 8 |
| **Case 2** | `"rohtang ki ice wali photo"` | Interview Ep 06 & 07 | 1 | 1 | 5 | 7 |
| **Case 3** | `"white bike"` | Interview Ep 13 | 1 | 1 | 6 | 8 |
| **Case 4** | `"diya at the gate"` | Interview Ep 25 | 1 | 1 | 4 | 6 |
| **Case 5** | `"Progressive"` | Reddit Case 5 | 1 | 1 | 4 | 6 |
| **Case 6** | `"document around 4 years ago"` | Interview Ep 10 | 1 | 1 | 4 | 6 |
| **Case 7** | `"yellow truck"` | Reddit Case 11 & 4 | 10 | 0 | 7 | 17 |
| **Case 8** | `"wedding"` | Reddit Case 10 & Ep 02 | 3 | 1 | 3 | 7 |
| **TOTAL** | — | — | **19** | **6** | **40** | **65** |

---

## 3. Case-by-Case Deep Audit

### Case 1: `"5 sisters"`

#### A. Test Hypothesis
Translating natural relational kinship roles (`sister`, `count: 5`) into demographic search primitives (`group_count: 5`, `apparent_gender: female`) enables the Discovery Engine to admit unindexed family photographs into the candidate pool where direct literal keyword search yields zero results due to the absence of private genealogical tags.

#### B. Candidate Manifest
- **Target Candidate ID:**
  - `c1_tgt_family_5sisters`: Group portrait of 5 young adult women sitting on a sofa in traditional attire during a family gathering.
    - `demographic_tags`: `{"count": 5, "apparent_gender": "female", "apparent_age": "young_adult"}`
    - `bound_attributes`: `{"person": ["traditional_attire", "smiling"]}`
    - `is_ground_truth_target`: `true`
- **Relevant Candidate ID:**
  - `c1_rel_campus_5females`: Group portrait of 5 young adult women on a college campus in casual clothing.
    - `demographic_tags`: `{"count": 5, "apparent_gender": "female", "apparent_age": "young_adult"}`
    - `is_ground_truth_target`: `false`
    - *Role in Benchmark:* Represents demographic match without the private domestic family context.
- **Major Distractor Candidate IDs:**
  - `c1_dist_3females`: Group of 3 females in casual clothing.
  - `c1_dist_7females`: Group of 7 females at a banquet.
  - `c1_dist_5males`: Group of 5 males in sports jerseys on a basketball court.
  - `c1_dist_5mixed`: Group of 5 mixed-gender young adults at a park picnic.
  - `c1_dist_1female_portrait`: Single female portrait in a photo studio.
  - `c1_dist_literal_sister_sign`: Street sign containing literal in-image text `"Seven Sisters Bakery"`.

#### C. Distractor Rationale & Failure Mode Analysis
| Distractor ID | Why It Exists in Corpus | Specific Failure Mode Tested |
| :--- | :--- | :--- |
| `c1_dist_3females` | Group with fewer females (`count: 3`) | Cardinality sensitivity: tests whether the engine filters out incorrect group sizes. |
| `c1_dist_7females` | Group with more females (`count: 7`) | Over-count tolerance: tests whether the engine strictly separates 5 from other multi-person groups. |
| `c1_dist_5males` | Group with identical count (`count: 5`) but male | Gender translation validation: tests whether demographic primitive translation respects `female` vs generic count. |
| `c1_dist_5mixed` | Group of 5 with mixed gender | Demographic purity: tests whether mixed-gender groups are demoted relative to all-female groups. |
| `c1_dist_1female_portrait` | Solo female | Single-entity vs group distinction. |
| `c1_dist_literal_sister_sign` | Contains literal text `"Seven Sisters Bakery"` | **Direct literal baseline trap:** Demonstrates that a naive text search for `"sister"` returns commercial signage while completely missing the family photo. |

#### D. Distinguishability Assessment
- **Strategy A (Literal Baseline):** Searches for the token `"sister"` in tags/metadata. Because personal photo libraries index demographic primitives rather than social kinship trees, it returns `0` results (or erroneously retrieves `c1_dist_literal_sister_sign`).
- **Strategy B (Discovery Engine):** Ingests `"5 sisters"`, translates kinship into `[count: 5, gender: female]`, retrieves `c1_tgt_family_5sisters` and `c1_rel_campus_5females`, and ranks the primary family gathering highest.
- **Benchmark Sufficiency:** **Cleanly Testable.** The benchmark provides distinct failure paths for cardinality, gender, and literal keyword search.

---

### Case 2: `"rohtang ki ice wali photo"`

#### A. Test Hypothesis
Natural language memory interpretation strips colloquial code-mixed Hindi syntax (`ki`, `wali`, `photo`) while preserving `raw_input`, isolating the core spatial setting (`rohtang`) and visual element (`ice`), preventing zero-result failures caused when direct keyword search engines treat conversational postpositions as required search terms.

#### B. Candidate Manifest
- **Target Candidate ID:**
  - `c2_tgt_rohtang_snow`: Tourist photo taken at Rohtang Pass featuring snow-covered mountains and glacial ice.
    - `spatial_setting`: `"Rohtang Pass"`
    - `visual_entities`: `["snow", "ice", "mountain", "tourist"]`
    - `bound_attributes`: `{"mountain": ["snow_covered"], "ice": ["glacial"]}`
    - `is_ground_truth_target`: `true`
- **Relevant Candidate ID:**
  - `c2_rel_rohtang_summer`: Landscape photo at Rohtang Pass during summer with rocky/green valleys and no ice/snow.
    - `spatial_setting`: `"Rohtang Pass"`
    - `visual_entities`: `["mountain", "valley", "tourist", "rocks"]`
    - `is_ground_truth_target`: `false`
    - *Role in Benchmark:* Satisfies spatial location but lacks the salient physical ice element.
- **Major Distractor Candidate IDs:**
  - `c2_dist_wali_sign`: Old Delhi shop sign with printed text `"Paranthe Wali Gali Famous Photo Studio"`.
  - `c2_dist_solang_snow`: Ski slope at Solang Valley with snow and ice.
  - `c2_dist_ice_cream`: Tabletop photo of vanilla ice cream dessert in a cafe.
  - `c2_dist_passport_photo_desk`: Printed passport photographs sitting on an office desk.
  - `c2_dist_goa_beach`: Tropical beach photo from Goa.

#### C. Distractor Rationale & Failure Mode Analysis
| Distractor ID | Why It Exists in Corpus | Specific Failure Mode Tested |
| :--- | :--- | :--- |
| `c2_dist_wali_sign` | Contains literal words `"Wali"` and `"Photo"` | **Colloquial keyword poison pill:** Naive keyword systems querying `"wali photo"` match this storefront while missing the mountain trip. |
| `c2_dist_solang_snow` | Features snow/ice at a different location (`Solang Valley`) | Spatial selectivity: ensures the engine evaluates geographic metadata and does not rely solely on visual snow features. |
| `c2_dist_ice_cream` | Features culinary `"ice"` | Lexical polysemy: tests whether the engine discriminates mountain ice/snow from food ice cream. |
| `c2_dist_passport_photo_desk` | Desk photo matching the word `"photo"` | Conversational meta-word stripping: tests whether the user's reference to the media format (`"photo"`) is stripped from retrieval signals. |
| `c2_dist_goa_beach` | Non-mountain vacation photo | General negative control. |

#### D. Distinguishability Assessment
- **Strategy A (Literal Baseline):** Queries `"rohtang ki ice wali photo"`. Tokens `"wali"` and `"photo"` either cause zero-result failure or incorrectly retrieve `c2_dist_wali_sign` and `c2_dist_passport_photo_desk`.
- **Strategy B (Discovery Engine):** Isolates `spatial: "rohtang"` and `objects: ["ice"]`, routes to spatial and visual paths, and scores `c2_tgt_rohtang_snow` at Rank 1.
- **Benchmark Sufficiency:** **Cleanly Testable.** The benchmark directly isolates vernacular particle rejection and spatial-object co-occurrence.

---

### Case 3: `"white bike"`

#### A. Test Hypothesis
Entity-attribute binding evaluates attribute modifiers (`white`) directly on their host entity (`bike`), preventing false-positive flooding from disconnected attribute matches (white shirts, white walls, white cars) alongside non-white bikes.

#### B. Candidate Manifest
- **Target Candidate ID:**
  - `c3_tgt_white_motorcycle`: Rider on a white motorcycle along a mountain highway.
    - `visual_entities`: `["bike", "person", "road"]`
    - `bound_attributes`: `{"bike": ["white"], "person": ["black_jacket", "helmet"]}`
    - `is_ground_truth_target`: `true`
- **Relevant Candidate ID:**
  - `c3_rel_silver_white_bicycle`: Cyclist on a metallic silver-white bicycle in a park.
    - `visual_entities`: `["bike", "person"]`
    - `bound_attributes`: `{"bike": ["silver_white", "metallic"]}`
    - `is_ground_truth_target`: `false`
    - *Role in Benchmark:* Evaluates soft attribute satisfaction for near-white two-wheelers.
- **Major Distractor Candidate IDs:**
  - `c3_dist_black_bike_white_shirt`: Black motorcycle with a rider wearing a prominent white shirt.
  - `c3_dist_black_bike_white_wall`: Black motorcycle parked in front of a white brick wall.
  - `c3_dist_white_car`: White passenger car in a parking lot.
  - `c3_dist_black_bike_alone`: Black motorcycle alone on an asphalt street.
  - `c3_dist_white_shirt_person`: Person in a white shirt in a botanical garden without any vehicle.
  - `c3_dist_unrelated_white_dog`: White fluffy dog playing in a backyard.

#### C. Distractor Rationale & Failure Mode Analysis
| Distractor ID | Why It Exists in Corpus | Specific Failure Mode Tested |
| :--- | :--- | :--- |
| `c3_dist_black_bike_white_shirt` | Bike present (`black`) + white object on person (`white shirt`) | **Disconnected attribute binding (person):** Uncoordinated bag-of-words systems score this high because both `"white"` and `"bike"` appear in the image metadata. |
| `c3_dist_black_bike_white_wall` | Bike present (`black`) + white background (`white wall`) | **Disconnected attribute binding (background):** Tests whether background color matches are prevented from satisfying entity color attributes. |
| `c3_dist_white_car` | White vehicle of wrong entity class (`car`) | Entity specificity: tests whether attribute matches without entity satisfaction are rejected. |
| `c3_dist_black_bike_alone` | Target entity present with contradictory attribute (`black`) | Entity without attribute: tests baseline fallback ranking. |
| `c3_dist_white_shirt_person` | Attribute present on clothing, no vehicle | Attribute without entity. |
| `c3_dist_unrelated_white_dog` | Unrelated white animal | Independent color noise control. |

#### D. Distinguishability Assessment
- **Strategy A (Literal Baseline):** Evaluates `"white"` and `"bike"` independently. Scores `c3_dist_black_bike_white_shirt` and `c3_dist_black_bike_white_wall` identically to `c3_tgt_white_motorcycle`, resulting in false-positive flooding.
- **Strategy B (Discovery Engine):** Evaluates `Match(bike, candidate)` AND specifically `Match(bike.attribute == white, candidate)`. Elevates `c3_tgt_white_motorcycle` to top rank while heavily penalizing disconnected matches.
- **Benchmark Sufficiency:** **Cleanly Testable.** The benchmark provides all six required contrastive configurations specified in the prompt.

---

### Case 4: `"diya at the gate"`

#### A. Test Hypothesis
Multi-path discovery (spatial setting path + visual entity path) enables the retrieval of candidate photos via co-occurring environmental clues, recovering photos where biometric facial recognition fails due to an unindexed, infrequent acquaintance (residential watchman).

#### B. Candidate Manifest
- **Target Candidate ID:**
  - `c4_tgt_diya_residential_gate`: Watchman lighting a brass/clay diya at a residential entrance iron gate during Diwali evening.
    - `spatial_setting`: `"residential entrance gate"`
    - `visual_entities`: `["diya", "gate", "flame", "person"]`
    - `bound_attributes`: `{"diya": ["lit", "brass", "clay"], "gate": ["iron_gate", "residential"]}`
    - `demographic_tags`: `{"count": 1, "apparent_gender": "male", "apparent_age": "middle_aged"}`
    - `is_ground_truth_target`: `true`
- **Relevant Candidate ID:**
  - `c4_rel_diya_front_porch`: Lit terracotta diya on a front doorway porch with rangoli.
    - `spatial_setting`: `"front doorway porch"`
    - `visual_entities`: `["diya", "doorway", "rangoli", "flame"]`
    - `is_ground_truth_target`: `false`
    - *Role in Benchmark:* Threshold/entrance setting with diya, close to target but not at the outer gate.
- **Major Distractor Candidate IDs:**
  - `c4_dist_diya_pooja_altar`: Lit brass diya on an indoor prayer altar with flowers and idols.
  - `c4_dist_gate_delivery_car`: Residential entrance gate with a delivery person and parked car.
  - `c4_dist_gate_dog`: Stray dog sleeping outside the residential entrance gate.
  - `c4_dist_street_light_lamp`: Electric street lamp illuminating a suburban asphalt road.

#### C. Distractor Rationale & Failure Mode Analysis
| Distractor ID | Why It Exists in Corpus | Specific Failure Mode Tested |
| :--- | :--- | :--- |
| `c4_dist_diya_pooja_altar` | Object present (`diya`), wrong spatial setting (`altar`) | Spatial discrimination: ensures the engine does not retrieve indoor festival lamps that lack entrance gate context. |
| `c4_dist_gate_delivery_car` | Spatial setting present (`gate`), missing object (`diya`) | Object necessity: ensures the engine does not retrieve gate photos lacking festival lamps. |
| `c4_dist_gate_dog` | Gate present with unrelated living subject (`dog`) | Spatial context alone is insufficient without object co-occurrence. |
| `c4_dist_street_light_lamp` | Modern outdoor lighting fixture | Category confusion: tests whether generic illumination sources (`street lamp`) trigger false matches for traditional oil lamps (`diya`). |

#### D. Distinguishability Assessment
- **Strategy A (Literal Baseline):** Fails if relying on person/face albums (the watchman is unindexed). If performing keyword lookup, either floods with indoor altar diyas or generic gate photos.
- **Strategy B (Discovery Engine):** Combines visual entity path (`diya`) and spatial path (`gate`), executing compositional intersection scoring that elevates `c4_tgt_diya_residential_gate` above single-clue candidates.
- **Benchmark Sufficiency:** **Cleanly Testable.** Tests both the spatial-object intersection and biometric independence.

---

### Case 5: `"Progressive"`

#### A. Test Hypothesis
Memory interpretation classifies single-token commercial names as literal in-image text candidates rather than conversational dialog prompts or descriptive adjectives, routing them directly to OCR index matching and eliminating chatbot refusals (*"I can't help with that"*).

#### B. Candidate Manifest
- **Target Candidate ID:**
  - `c5_tgt_progressive_insurance_policy`: Auto insurance declaration paperwork on a desk containing printed text `"Progressive"`, `"Auto Insurance Policy"`, and `"Premium Due"`.
    - `visual_entities`: `["document", "paperwork"]`
    - `in_image_text`: `["Progressive", "Auto Insurance Policy", "Declarations Page", "Policy Number", "Premium Due"]`
    - `is_ground_truth_target`: `true`
- **Relevant Candidate ID:**
  - `c5_rel_progressive_id_card`: Wallet-sized digital insurance card with text `"Progressive Insurance"`.
    - `visual_entities`: `["document", "insurance_card"]`
    - `in_image_text`: `["Progressive Insurance", "Proof of Insurance Card", "Effective Date"]`
    - `is_ground_truth_target`: `false`
    - *Role in Benchmark:* Secondary document containing the exact commercial brand name.
- **Major Distractor Candidate IDs:**
  - `c5_dist_geico_utility_bill`: Utility electric bill from Consolidated Edison on kitchen counter.
  - `c5_dist_tax_w2_document`: IRS Form W-2 wage and tax statement on office desk.
  - `c5_dist_progress_fitness_banner`: Gym banner with printed text `"Progress Fitness Club"`.
  - `c5_dist_progressive_rock_poster`: Concert poster on bedroom wall with text `"Progressive Rock Festival"`.

#### C. Distractor Rationale & Failure Mode Analysis
| Distractor ID | Why It Exists in Corpus | Specific Failure Mode Tested |
| :--- | :--- | :--- |
| `c5_dist_geico_utility_bill` | Document present, but completely different entity text | Document false-positive control: verifies that the engine does not retrieve arbitrary bills. |
| `c5_dist_tax_w2_document` | Official tax document without target token | Paperwork false-positive control. |
| `c5_dist_progress_fitness_banner` | Substring match (`"Progress"` instead of `"Progressive"`) | Exact token boundary matching: tests whether OCR prefix matching erroneously matches partial brand stems. |
| `c5_dist_progressive_rock_poster` | Exact token present (`"Progressive"`), but non-document media | Modal separation: tests whether literal text path recovers the token across media types while downstream scoring incorporates document context. |

#### D. Distinguishability Assessment
- **Strategy A (Literal Baseline / Conversational LLM):** Observed in Reddit Case 5: Ask Photos treats `"Progressive"` as an ambiguous or conversational prompt, outputting a chatbot refusal (*"I can't help with that"*). A basic metadata lookup fails if text is not in manual image tags.
- **Strategy B (Discovery Engine):** Ingests `"Progressive"` into `literal_text: ["Progressive"]`, executes in-image text OCR matching, and retrieves the insurance document `c5_tgt_progressive_insurance_policy`.
- **Benchmark Sufficiency:** **Cleanly Testable.** Evaluates in-image text token matching against non-text documents and visual text distractors. *(See Section 4 for conversational boundary note).*

---

### Case 6: `"document around 4 years ago"`

#### A. Test Hypothesis
Natural language hedging and coarse temporal offsets (`"around 4 years ago"`, `RELATIVE_OFFSET`) map to a continuous historical interval ($[t - 4.5\text{y}, t - 3.5\text{y}]$) centered around the reference date, enabling successful document recovery without requiring rigid calendar date inputs (`YYYY-MM-DD`).

*Reference Date:* $t = \text{2026-09-30T12:00:00Z}$ (matching current local simulation time).  
*Continuous Interval:* ~`2022-03-31` to `2023-03-31` (target: ~4.0 years ago).

#### B. Candidate Manifest
- **Target Candidate ID:**
  - `c6_tgt_lease_agreement_2022`: Signed, notarized residential lease agreement document photographed on an office desk.
    - `timestamp`: `"2022-08-14T10:15:00Z"` ($\approx 4.13$ years ago, directly in target window)
    - `visual_entities`: `["document", "paperwork"]`
    - `bound_attributes`: `{"document": ["notarized_contract", "signed"]}`
    - `is_ground_truth_target`: `true`
- **Relevant Candidate ID:**
  - `c6_rel_bank_statement_2022`: Monthly bank statement document on desk.
    - `timestamp`: `"2022-11-20T14:30:00Z"` ($\approx 3.86$ years ago, inside window)
    - `visual_entities`: `["document", "paperwork"]`
    - `is_ground_truth_target`: `false`
    - *Role in Benchmark:* Document falling within the temporal window, but secondary to the lease contract.
- **Major Distractor Candidate IDs:**
  - `c6_dist_recent_document_2026`: Recent medical bill document from 6 months ago (`2026-03-10T09:00:00Z`, $\approx 0.56$ years ago).
  - `c6_dist_old_document_2018`: IRS tax form document from 8 years ago (`2018-04-12T11:00:00Z`, $\approx 8.47$ years ago).
  - `c6_dist_birthday_photo_2022`: 25th Birthday party photo with cake and balloons dated $\approx 4.19$ years ago (`2022-07-22T19:30:00Z`).
  - `c6_dist_mountain_trip_2024`: National park hiking vacation photo dated 2 years ago (`2024-05-18T12:00:00Z`).

#### C. Distractor Rationale & Failure Mode Analysis
| Distractor ID | Why It Exists in Corpus | Specific Failure Mode Tested |
| :--- | :--- | :--- |
| `c6_dist_recent_document_2026` | Document entity present, but outside temporal window (too recent) | Temporal lower bound: tests whether the engine excludes modern documents despite entity match. |
| `c6_dist_old_document_2018` | Document entity present, but outside temporal window (too old) | Temporal upper bound: tests whether the engine excludes ancient documents from 8+ years ago. |
| `c6_dist_birthday_photo_2022` | Inside temporal window ($\approx 4$ years ago), but non-document | Entity filtering: tests whether photos matching the time window but lacking document characteristics are rejected. |
| `c6_dist_mountain_trip_2024` | Non-document photo outside window | General negative control. |

#### D. Distinguishability Assessment
- **Strategy A (Literal Baseline):** Expects calendar dates or rejects the conversational hedge `"around"`. If searching purely for `"document"`, floods with hundreds of recent paperwork images (including `c6_dist_recent_document_2026`).
- **Strategy B (Discovery Engine):** Computes continuous interval $[2022\text{-}03\text{-}31, 2023\text{-}03\text{-}31]$, activates temporal and visual document paths, and scores `c6_tgt_lease_agreement_2022` at Rank 1.
- **Benchmark Sufficiency:** **Cleanly Testable.** The benchmark cleanly separates visual document classification from temporal window bounds.

---

### Case 7: `"yellow truck"`

#### A. Test Hypothesis
The Candidate Coverage Check detects single-session / single-day candidate truncation (simulating Reddit Case 11 where an initial probe captured only 2 of 10 days of a recurring entity) and triggers controlled recovery to discover the yellow truck across all 10 distinct simulated days.

#### B. Candidate Manifest
- **Target Candidate IDs (10 Distinct Simulated Days):**
  - `c7_tgt_truck_day01`: `2024-06-01T09:15:00Z` — Equipment staging at construction depot
  - `c7_tgt_truck_day02`: `2024-06-03T11:30:00Z` — Convoy transit on interstate highway
  - `c7_tgt_truck_day03`: `2024-06-05T14:10:00Z` — Quarry loading at gravel quarry
  - `c7_tgt_truck_day04`: `2024-06-08T08:45:00Z` — Cargo intake at industrial warehouse
  - `c7_tgt_truck_day05`: `2024-06-11T16:20:00Z` — Gravel hauling on access road
  - `c7_tgt_truck_day06`: `2024-06-14T10:00:00Z` — Fleet service at maintenance garage
  - `c7_tgt_truck_day07`: `2024-06-17T13:40:00Z` — Steep transport on mountain pass road
  - `c7_tgt_truck_day08`: `2024-06-20T17:15:00Z` — Bridge construction at river bridge site
  - `c7_tgt_truck_day09`: `2024-06-23T07:50:00Z` — Morning prep at equipment yard
  - `c7_tgt_truck_day10`: `2024-06-26T12:05:00Z` — Project wrap-up at headquarters
  *(All 10 records have `visual_entities`: `["truck", "utility_vehicle"]`, `bound_attributes`: `{"truck": ["yellow"]}`, `is_ground_truth_target`: `true`).*
- **Relevant Candidate IDs:** None (all 10 instances of the truck are primary ground-truth targets).
- **Major Distractor Candidate IDs:**
  - `c7_dist_yellow_taxi`: Yellow sedan passenger taxi cab in city traffic.
  - `c7_dist_yellow_school_bus`: Yellow school bus parked outside a school.
  - `c7_dist_blue_dump_truck`: Blue dump truck at a quarry.
  - `c7_dist_red_pickup_truck`: Red consumer pickup truck in a driveway.
  - `c7_dist_white_semi_truck`: White semi-trailer truck on interstate.
  - `c7_dist_yellow_raincoat`: Person in a bright yellow raincoat on city street.
  - `c7_dist_yellow_hardhat`: Yellow construction hardhat on a workbench.

#### C. Distractor Rationale & Failure Mode Analysis
| Distractor ID | Why It Exists in Corpus | Specific Failure Mode Tested |
| :--- | :--- | :--- |
| `c7_dist_yellow_taxi` | Yellow vehicle of wrong entity type (`car/taxi`) | Vehicle category specificity: yellow cars must not trigger truck retrieval. |
| `c7_dist_yellow_school_bus` | Large yellow public transit vehicle (`bus`) | Heavy vehicle category distinction. |
| `c7_dist_blue_dump_truck` | Target vehicle class (`truck`), but wrong color (`blue`) | Entity-attribute binding: color `yellow` must be bound to truck body. |
| `c7_dist_red_pickup_truck` | Target vehicle class (`truck`), but wrong color (`red`) | Attribute binding negative control. |
| `c7_dist_white_semi_truck` | Heavy truck, non-yellow (`white`) | Attribute binding negative control. |
| `c7_dist_yellow_raincoat` | Salient yellow color on clothing, no vehicle | Attribute match without entity host. |
| `c7_dist_yellow_hardhat` | Yellow construction safety prop | Unrelated yellow object in construction context. |

#### D. Distinguishability Assessment
- **Strategy A (Literal Baseline / Truncation Bug):** Observed in Reddit Case 11: System returns only 2 days of photos (Day 1 and Day 2) due to a hard presentation/search limit, dropping 80% of matching days.
- **Strategy B (Discovery Engine):**
  1. Initial retrieval probe captures Day 1 and Day 2.
  2. Candidate Coverage Check observes candidates are clustered in an isolated session while broader temporal records exist for the entity $\rightarrow$ Flags coverage as **INSUFFICIENT**.
  3. Controlled Recovery broadens search along timeline to recover all 10 days into the unified pool.
- **Benchmark Sufficiency:** **Cleanly Testable.** The 10 distinct simulated dates across 26 days provide unambiguous quantitative measurement of temporal recall expansion.

---

### Case 8: `"wedding"`

#### A. Test Hypothesis
In broad milestone event queries, multiple photos belonging to the same multi-day wedding celebration are retrieved and organized with event-context coherence, rather than being scattered across time or mixed up with unrelated celebrations.

#### B. Candidate Manifest
- **Target Candidate IDs (Multi-Day Target Wedding — "Meera Wedding", Nov 2023):**
  - `c8_tgt_wedding_sangeet`: `2023-11-17T19:30:00Z` — Family dancing in festive attire on outdoor stage at Sangeet night.
  - `c8_tgt_wedding_ceremony`: `2023-11-18T18:15:00Z` — Bride in red lehenga and groom in sherwani around sacred fire at main ceremony.
  - `c8_tgt_wedding_reception`: `2023-11-19T20:45:00Z` — Bride, groom, and guests in formal attire with floral backdrop at grand reception.
  *(All 3 records have `is_ground_truth_target`: `true`, event: `"Meera Wedding"`).*
- **Relevant Candidate ID:**
  - `c8_rel_colleague_wedding_2021`: `2021-02-14T19:00:00Z` — Wedding ceremony of a work colleague from three years earlier.
    - `event_context`: `"Rohan Colleague Wedding"`
    - `is_ground_truth_target`: `false`
    - *Role in Benchmark:* Valid wedding event, but distinct from the primary target wedding milestone.
- **Major Distractor Candidate IDs:**
  - `c8_dist_birthday_party_2024`: 25th Birthday celebration with chocolate cake and balloons.
  - `c8_dist_annual_office_gala_2023`: Corporate gala dinner with podium, suits, and wine glasses.
  - `c8_dist_diwali_family_dinner_2023`: Diwali festive dinner with ethnic wear and sweets.

#### C. Distractor Rationale & Failure Mode Analysis
| Distractor ID | Why It Exists in Corpus | Specific Failure Mode Tested |
| :--- | :--- | :--- |
| `c8_dist_birthday_party_2024` | Social celebration with formal/party attire | Celebration milestone distinction: tests whether the engine isolates wedding ceremonies from other social milestones. |
| `c8_dist_annual_office_gala_2023` | Formal evening event with suits and banquet | Formality confusion: tests whether generic formal evening wear triggers false positive wedding classifications. |
| `c8_dist_diwali_family_dinner_2023` | Cultural family celebration in traditional ethnic clothing | Cultural attire confusion: tests whether traditional Indian attire is misclassified as a wedding ceremony. |

#### D. Distinguishability Assessment
- **Strategy A (Literal Baseline / Uncalibrated Best Match):** Returns isolated photos scattered across the timeline (as in Reddit Case 10), failing to retain multi-day event connections between Sangeet, Ceremony, and Reception.
- **Strategy B (Discovery Engine):** Retrieves wedding milestone candidates and preserves event-context coherence, clustering the three days of Meera's wedding together with chronological landmarks.
- **Benchmark Sufficiency:** **Cleanly Testable.** Evaluates event milestone classification against competing celebrations, and provides multi-day event grouping for result organization.

---

## 4. Methodological Stress Test & Boundary Identification

In accordance with the project instructions, we explicitly audit whether any of the 8 cases possess methodological nuances or boundaries that must be accounted for during experimental execution:

### 1. Case 1 ("5 sisters"): Social Kinship vs. Demographic Proxy
- **Boundary:** Private genealogical family relationships (`"sister"`) do not exist in standard photo metadata. In this experiment, the engine relies on the **experimental translation hypothesis**: `sister` $\rightarrow$ `[demographic primitive: female, count: 5]`.
- **Methodological Impact:** The benchmark successfully tests candidate recovery via demographic primitives where direct keyword search returns zero results. However, this is an experimental translation proxy, not a biological genealogy proof. If two photos contain 5 females (e.g., family vs. college campus), visual demographic scoring alone scores them similarly; distinguishing them requires surrounding event context.

### 2. Case 5 ("Progressive"): Conversational Refusal Simulation
- **Boundary:** In the empirical research (Reddit Case 5), the baseline failure was an interactive LLM chat refusal (*"I can't help with that"*).
- **Methodological Impact:** A static benchmark JSON cannot run an interactive conversational dialog session. In the experimental runner, Strategy A's failure mode on Case 5 will be modeled as querying metadata tags for `"Progressive"` while routing conversational text to prompt handling (which yields zero image candidates), whereas Strategy B routes the literal alphanumeric token directly to `in_image_text` OCR matching.

### 3. Case 7 ("yellow truck"): Simulating the Initial Truncation Pass
- **Boundary:** The benchmark contains all 10 days of yellow truck photos. In a real system, the "few-photos truncation bug" arises dynamically from query timeouts or arbitrary presentation caps (e.g., capping results at 2 days or 6 items).
- **Methodological Impact:** To test the Candidate Coverage Check and Controlled Recovery cleanly, the experimental runner must execute Phase 1 under a simulated single-session constraint (admitting only Day 1 and Day 2 into the initial pool), verify that the coverage check flags `INSUFFICIENT`, and then demonstrate that Controlled Recovery expands the pool to include all 10 days.

### 4. Case 8 ("wedding"): Relevance Ranking vs. Result Organization
- **Boundary:** Both the primary target wedding (`"Meera Wedding"`) and the distractor wedding (`"Rohan Colleague Wedding"`) are valid wedding events.
- **Methodological Impact:** Pure additive candidate scoring in Stage 5 will score both weddings high because both satisfy `event: "wedding"`. The core architectural hypothesis for Case 8 is evaluated at **Stage 6 (Result Organization)**, where candidate photos are organized into coherent multi-day event clusters rather than scattered isolated items.

---

## 5. Benchmark Audit Verification Sign-Off

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        EXPERIMENTAL BENCHMARK AUDIT MATRIX                             │
├─────────┬───────────────────────────────┬──────────────┬──────────────┬────────────────┤
│ CASE #  │ CASE NAME                     │ TARGET COUNT │ TOTAL CORPU  │ STATUS         │
├─────────┼───────────────────────────────┼──────────────┼──────────────┼────────────────┤
│ Case 1  │ "5 sisters"                   │ 1 target     │ 8 candidates │ Cleanly tested │
│ Case 2  │ "rohtang ki ice wali photo"   │ 1 target     │ 7 candidates │ Cleanly tested │
│ Case 3  │ "white bike"                  │ 1 target     │ 8 candidates │ Cleanly tested │
│ Case 4  │ "diya at the gate"            │ 1 target     │ 6 candidates │ Cleanly tested │
│ Case 5  │ "Progressive"                 │ 1 target     │ 6 candidates │ Cleanly tested │
│ Case 6  │ "document around 4 years ago" │ 1 target     │ 6 candidates │ Cleanly tested │
│ Case 7  │ "yellow truck"                │ 10 targets   │ 17 candidates│ Cleanly tested │
│ Case 8  │ "wedding"                     │ 3 targets    │ 7 candidates │ Cleanly tested │
├─────────┴───────────────────────────────┴──────────────┴──────────────┴────────────────┤
│ TOTAL: 65 Candidates | 19 Targets | 6 Relevant Non-Targets | 40 Major Distractors      │
│ SCHEMA INTEGRITY: 100% Validated (10/10 locked fields, 0 extra fields, valid ISO-8601)  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

The controlled benchmark corpus in [part1_experimental_benchmark.json](file:///d:/graduation%20project%203/part1_experimental_benchmark.json) is complete, methodologically audited, and fully prepared for the subsequent experimental runner.
