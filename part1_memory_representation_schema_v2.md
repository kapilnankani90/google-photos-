# Part 1 — Memory Representation Schema (V2)

## 1. Purpose

The purpose of this document is to define a clean, evidence-grounded **V2 Memory Representation Schema** for **Part 1: Build an AI-Powered Discovery Engine**.

Following the rigorous audit conducted in [part1_memory_schema_audit.md](file:///d:/graduation%20project%203/part1_memory_schema_audit.md), this schema eliminates the over-modeled abstractions, speculative confidence enums, and foreign-key graph structures that were identified as premature. 

The schema establishes a simple, defensible representation of what human users naturally remember and express when trying to find an old photo. It bridges raw natural-language memory into an interpretable structured representation:

$$\text{RAW USER MEMORY INPUT} \longrightarrow \text{INTERPRETED MEMORY REPRESENTATION} \longrightarrow \text{[Discovery Engine Architecture]}$$

> [!IMPORTANT]
> **Strict Non-Technical Boundaries Maintained:**
> - This schema defines the **informational requirements** of memory representation.
> - It does **not** design candidate generation, vector search, lexical indexing, or ranking algorithms.
> - It does **not** select database technologies, embedding models, LLM frameworks, or system APIs.
> - It does **not** specify user interface layouts or interaction wireframes.
> - Technical implementation decisions are strictly deferred to subsequent architectural phases.

---

## 2. Evidence Basis

This schema is derived strictly from the verified findings of:
1. **[part1_memory_schema_audit.md](file:///d:/graduation%20project%203/part1_memory_schema_audit.md):** Evidence-based evaluation establishing core capabilities versus premature hypotheses.
2. **[part1_combined_evidence.md](file:///d:/graduation%20project%203/part1_combined_evidence.md):** Consolidated research evidence base across public feedback and 1:1 user testing.
3. **[interview_behavioral_episodes.md](file:///d:/graduation%20project%203/interview_behavioral_episodes.md):** Step-by-step audit of 25 distinct real-world retrieval tasks across 6 smartphone users.
4. **[research_summary.md](file:///d:/graduation%20project%203/research_summary.md):** 61 pristine cases from Google Play Store reviews and Reddit technical community discussions.

---

## 3. Design Principles

The V2 schema is governed by six evidence-grounded principles:

### Principle 1: Separation of Raw Input and Interpreted Structure
The raw natural-language expression must always be preserved verbatim. Natural code-mixed particles (Hinglish `ki`, `wali`, `ke sath`), word order, and vernacular nuance must never be discarded or overwritten during interpretation.

### Principle 2: Compositional Binding Over Graph Foreign Keys
When attributes qualify entities (e.g. *"white bike"*, *"yellow suit"*, *"family yellow"*), they must be bound directly to the concept they describe. Complex multi-node graph ontologies with artificial entity IDs and foreign-key pointer tables are rejected as unnecessary engineering overhead.

### Principle 3: Relational Kinship Preservation
Human beings categorize people by social, familial, and occupational roles (`sister`, `cousin`, `brother`, `maid`, `watchman`, `colleague`). The representation must retain these roles directly rather than prematurely flattening them into generic third-person demographic tags (`girl`, `man`).

### Principle 4: Flexible Temporal Expressiveness Without Rigid Timestamps
Human memory recalls coarse intervals (`"2021"`), relative offsets (`"around 4 years ago"`), seasons (`"Holi 2020"`), or specific month/year milestones (`"July 2016"`). The schema must accommodate approximate and coarse time naturally without forcing conversion into rigid ISO timestamps.

### Principle 5: Literal OCR Text Segregation
Remembered printed text snippets (`"Progressive"`, `"bitcoin"`, `"I love being a man"`) must be represented as a distinct literal text dimension, preventing conversational models from confusing literal pixel text with abstract conceptual themes.

### Principle 6: Parsimony and Simplicity
Every field must reflect directly observed user search behavior. If an attribute can be represented compositionally as an entity modifier, it does not receive a dedicated top-level subsystem.

---

## 4. V2 Memory Representation

The V2 schema is structured into two clean layers:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              LAYER 1: USER MEMORY INPUT                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • raw_input: Verbatim natural-language expression as uttered/typed by the user         │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                     LAYER 2: INTERPRETED MEMORY REPRESENTATION                         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ • people:           List of person concepts [role/kinship, count, attributes, poss]    │
│ • events:           Milestone anchor [event_name, optional sub_event]                  │
│ • objects:          Salient physical items/props [name, attributes, poss]              │
│ • actions:          Dynamic activities / physical verbs / poses                        │
│ • temporal:         Time anchor [raw_time_expression, coarse_value, temporal_nature]   │
│ • literal_text:     Verbatim in-image OCR text snippets                                │
│ • spatial_setting:  (Supporting) Broad geographic or architectural landscape           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### JSON-Schema Specification of V2 Memory Representation

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "V2MemoryRepresentation",
  "description": "Evidence-grounded memory representation schema for AI-powered photo retrieval.",
  "type": "object",
  "properties": {
    "raw_input": {
      "type": "string",
      "description": "Verbatim user query or natural-language memory description exactly as provided."
    },
    "people": {
      "type": "array",
      "description": "People recalled by social, familial, or occupational role.",
      "items": {
        "type": "object",
        "properties": {
          "role": { "type": "string", "description": "Kinship or social role (e.g., sister, cousin, brother, maid, watchman, colleague)." },
          "count": { "type": "integer", "description": "Explicit group count if recalled (e.g., 5 in '5 sisters', 2 in 'two ladies')." },
          "attributes": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Descriptive visual or clothing modifiers bound to this person/group (e.g., ['yellow suit'], ['blue outfit'])."
          },
          "possessive": { "type": "string", "description": "Possessive marker if expressed (e.g., 'my', 'our')." }
        },
        "required": ["role"]
      }
    },
    "events": {
      "type": "object",
      "description": "Milestone event, cultural celebration, or social occasion.",
      "properties": {
        "event_name": { "type": "string", "description": "Primary event name (e.g., wedding, diwali, farewell, birthday, holi, engagement)." },
        "sub_event": { "type": "string", "description": "Optional specific ritual or sub-phase (e.g., haldi, rehearsal, farewell lunch)." }
      },
      "required": ["event_name"],
      "additionalProperties": false
    },
    "objects": {
      "type": "array",
      "description": "Salient physical props, vehicles, food preparations, or utility documents.",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string", "description": "Name of physical object or document (e.g., cake, bike, papaya, ring box, diya, truck, boarding pass)." },
          "attributes": {
            "type": "array",
            "items": { "type": "string" },
            "description": "Descriptive visual modifiers bound directly to this object (e.g., ['white'] for bike, ['yellow'] for truck, ['steel plate'] for cake)."
          },
          "possessive": { "type": "string", "description": "Possessive marker if expressed (e.g., 'my', 'our')." }
        },
        "required": ["name"]
      }
    },
    "actions": {
      "type": "array",
      "description": "Dynamic activities, physical sports, interactions, or bodily poses.",
      "items": {
        "type": "string",
        "description": "Specific action verb or pose description (e.g., 'rafting', 'skiing', 'lighting diya', 'peeling papaya', 'arms crossed')."
      }
    },
    "temporal": {
      "type": "object",
      "description": "Coarse calendar, relative elapsed, or specific temporal anchor.",
      "properties": {
        "raw_time_expression": { "type": "string", "description": "Verbatim temporal phrase (e.g., 'around 4 years ago', '2021', 'July 2016', 'Holi 2020')." },
        "coarse_value": { "type": "string", "description": "Extracted year or coarse era if identifiable (e.g., '2021', '2016', '4 years ago')." },
        "temporal_nature": {
          "type": "string",
          "enum": ["COARSE_YEAR_ERA", "RELATIVE_OFFSET", "SEASON_EVENT_BOUND", "EXACT_MONTH_YEAR"],
          "description": "Broad characterization of the temporal anchor without imposing rigid timestamps."
        }
      },
      "required": ["raw_time_expression"],
      "additionalProperties": false
    },
    "literal_text": {
      "type": "array",
      "description": "Literal alphanumeric text remembered as physically printed on an object, document, or screen.",
      "items": {
        "type": "string",
        "description": "Exact text snippet remembered by the user (e.g., 'Progressive', 'bitcoin', 'I love being a man')."
      }
    },
    "spatial_setting": {
      "type": "string",
      "description": "Broad geographic destination, landscape type, or architectural boundary (e.g., 'mountain', 'beach', 'gate', 'rohtang', 'Mussoorie')."
    }
  },
  "required": ["raw_input"],
  "additionalProperties": false
}
```

---

## 5. Field Definitions

Below is the definitive audit-grounded definition for every field in the V2 schema.

---

### 1. `raw_input`
- **Meaning:** The verbatim natural-language memory description or query as entered or uttered by the user.
- **Example:** `"rohtang ki ice wali photo"`, `"5 sisters"`, `"brother on white bike at cousin's wedding"`, `"July 2016"`, `"Progressive"`.
- **Evidence Basis:** Observed across all 25 interview tasks (Ep 01–25) and all 61 pristine public cases. Crucial for preserving vernacular syntax, Hinglish particles (`ki`, `wali`, `ke sath`), and word order.
- **Status:** **CORE**

---

### 2. `people`
- **Meaning:** Human individuals or social groups identified by relational kinship, familial role, social position, or demographic count, with bound visual modifiers.
- **Subfields:**
  - `role`: The relational kinship or social role (`sister`, `cousin`, `brother`, `maid`, `watchman`, `colleague`, `friends`).
  - `count`: Explicit cardinality when a group size is recalled (`5` in *"5 sisters"*, `2` in *"two ladies"*).
  - `attributes`: Visual or clothing descriptions bound directly to this person/group (`['yellow suit']`, `['blue outfit']`, `['mustache']`).
  - `possessive`: Possessive attachment (`'my'`, `'our'`).
- **Example:**
  ```json
  {
    "role": "sister",
    "count": 5,
    "attributes": []
  }
  ```
- **Evidence Basis:** 
  - Ep 02: Candidate 1 recalled `"cousin"` in `"YELLOW SUIT"`.
  - Ep 05: Candidate 2 recalled `"5 sisters"`.
  - Ep 08: Candidate 2 recalled domestic help: `"durga ke sath picture jo meri maid hai"`.
  - Ep 09: Candidate 2 recalled elderly relatives: `"two ladies with blue outfit"`.
  - Ep 13: Candidate 3 recalled `"brother"`.
  - Ep 25: Candidate 6 recalled `"watchman"`.
  - Reddit Case 8: `"new grandchild"`; Reddit Case 10: `"nephew"`.
- **Status:** **CORE**

---

### 3. `events`
- **Meaning:** The cultural, social, or corporate milestone or celebration framing the memory.
- **Subfields:**
  - `event_name`: The primary cultural or social occasion (`wedding`, `birthday`, `diwali`, `farewell`, `holi`, `engagement`).
  - `sub_event`: Optional specific ritual or phase (`haldi`, `farewell lunch`, `rehearsal`).
- **Example:**
  ```json
  {
    "event_name": "wedding",
    "sub_event": "haldi"
  }
  ```
- **Evidence Basis:** 
  - Ep 01: `"birthday photo"`.
  - Ep 02: `"wedding"`, `"HALDI"`, `"CEREMONY"`.
  - Ep 08: `"Holi 2020"`.
  - Ep 12: `"diwali"`.
  - Ep 18: `"best friend's engagement"`.
  - Ep 21: `"farewell lunch"`.
  - Ep 22: `"grandmother's 80th birthday"`.
  - Reddit Case 10: 4-day wedding event.
- **Status:** **CORE**

---

### 4. `objects`
- **Meaning:** Salient physical items, food preparations, vehicles, ceremonial props, or utility documents that anchor the memory.
- **Subfields:**
  - `name`: The physical item or document type (`cake`, `bike`, `papaya`, `diya`, `ring box`, `truck`, `document`, `boarding pass`).
  - `attributes`: Visual modifiers bound directly to the object (`['white']` for bike, `['yellow']` for truck, `['steel plate']` for cake).
  - `possessive`: Possessive marker if specified (`'my'`, `'our'`).
- **Example:**
  ```json
  {
    "name": "bike",
    "attributes": ["white"],
    "possessive": "my"
  }
  ```
- **Evidence Basis:** 
  - Ep 01: `"Cake"`.
  - Ep 13: `"white bike"`.
  - Ep 17: `"papaya"`.
  - Ep 18: `"ring box"`.
  - Ep 25: `"diya"`.
  - Ep 10: `"document"`.
  - Ep 24: `"boarding pass"`.
  - Reddit Case 3: `"cooling fan"`; Reddit Case 11: `"yellow truck"`.
- **Status:** **CORE**

---

### 5. `actions`
- **Meaning:** Dynamic physical activities, sports, interactions, or specific bodily poses.
- **Example:** `["rafting"]`, `["skiing"]`, `["lighting diya"]`, `["peeling papaya"]`, `["arms crossed"]`.
- **Evidence Basis:** 
  - Ep 06: `"sking photo"` (skiing on snow).
  - Ep 12: `"firecracker lighted in their hands"`.
  - Ep 17: `"peeling papaya to feed pet dog"`.
  - Ep 18: `"holding the ring box for a joke"`.
  - Ep 23: `"rafting"` (zero-friction #1 retrieval).
  - Ep 25: `"lighting a diya"`.
  - Reddit Case 12: `"picture of myself with my arms crossed"`.
- **Status:** **CORE**

---

### 6. `temporal`
- **Meaning:** The coarse, relative, or seasonal temporal anchor remembered by the user.
- **Subfields:**
  - `raw_time_expression`: Verbatim temporal phrase (`"around 4 years ago"`, `"2021"`, `"July 2016"`, `"Holi 2020"`).
  - `coarse_value`: Extracted year or relative offset (`"2021"`, `"4 years ago"`).
  - `temporal_nature`: Broad characterization (`COARSE_YEAR_ERA`, `RELATIVE_OFFSET`, `SEASON_EVENT_BOUND`, `EXACT_MONTH_YEAR`).
- **Example:**
  ```json
  {
    "raw_time_expression": "around 4 years ago",
    "coarse_value": "4 years ago",
    "temporal_nature": "RELATIVE_OFFSET"
  }
  ```
- **Evidence Basis:** 
  - Ep 07: `"2021"`.
  - Ep 08: `"Holi 2020"`.
  - Ep 10: `"around 4 years ago"`.
  - Reddit Case 7: `"July 2016"`.
  - Master Review Dataset: 12 pristine date queries.
- **Status:** **CORE**

---

### 7. `literal_text`
- **Meaning:** Literal alphanumeric characters, words, quotes, or codes remembered as printed on an object, document, or screen.
- **Example:** `["Progressive"]`, `["bitcoin"]`, `["I love being a man"]`.
- **Evidence Basis:** 
  - Ep 16: `"bitcoin"` (order confirmation ID).
  - Reddit Case 5: `"Progressive"` (insurance bill).
  - Reddit Case 6: `"I love being a man"` (text meme).
- **Status:** **CORE**

---

### 8. `spatial_setting`
- **Meaning:** Broad geographical destination, natural landscape, or built architectural boundary remembered as the setting.
- **Example:** `"mountain"`, `"beach"`, `"gate"`, `"rohtang"`, `"Mussoorie"`.
- **Evidence Basis:** 
  - Ep 06: `"rohtang"`.
  - Ep 11: `"mountain"`, `"Mussoorie"`.
  - Ep 15: `"beach"`, `"malwan"`.
  - Ep 25: `"gate"`.
- **Status:** **SUPPORTED (Non-Mandatory)**

---

## 6. Relationship Representation

The audit demonstrated that human memory binds descriptive attributes directly to specific entities, but does **not** operate as a formal graph database with artificial entity IDs and foreign-key tables.

The V2 schema achieves clean, defensible relationship modeling through **direct compositional nesting**:

### 1. Entity-Attribute Binding
Attributes are nested directly inside the entity (person or object) they describe:

```json
// Example: "white bike" (Candidate 3, Ep 13)
{
  "objects": [
    {
      "name": "bike",
      "attributes": ["white"]
    }
  ]
}
```

```json
// Example: "family in yellow" (Candidate 6, Ep 22)
{
  "people": [
    {
      "role": "family",
      "attributes": ["yellow"]
    }
  ]
}
```

### 2. Multi-Entity Co-occurrence
When multiple entities co-occur in memory, they are listed within their respective arrays. Their co-occurrence is preserved naturally within the same memory frame without requiring separate relational join tables:

```json
// Example: "diya at the gate" (Candidate 6, Ep 25)
{
  "objects": [{ "name": "diya" }],
  "spatial_setting": "gate",
  "actions": ["lighting diya"]
}
```

```json
// Example: "my cousin at sister's wedding wearing yellow suit" (Candidate 1, Ep 02)
{
  "people": [
    {
      "role": "cousin",
      "attributes": ["yellow suit"],
      "possessive": "my"
    }
  ],
  "events": {
    "event_name": "wedding",
    "sub_event": "haldi"
  }
}
```

This representation completely avoids artificial foreign keys (`actor_entity_ref`, `target_entity_ref`, `attached_to_entity_ref`, `entity_id`) while preserving the exact semantic relationships observed in real user behavior.

---

## 7. Temporal Representation

The audit established two key facts regarding temporal memory:
1. Users frequently remember approximate eras (`"around 4 years ago"`), coarse calendar years (`"2021"`), or specific month/year milestones (`"July 2016"`).
2. Users almost never recall exact calendar days (e.g. YYYY-MM-DD), but claims of "complete temporal amnesia" are false.

The V2 schema represents temporal anchors flexibly without forcing conversion into rigid ISO timestamps or artificial confidence enums:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          TEMPORAL EXPRESSION EXAMPLES                                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Coarse Calendar Year:                                                               │
│    raw_time_expression: "2021"                                                         │
│    coarse_value: "2021"                                                                │
│    temporal_nature: "COARSE_YEAR_ERA"                                                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 2. Relative Elapsed Offset:                                                            │
│    raw_time_expression: "around 4 years ago"                                           │
│    coarse_value: "4 years ago"                                                         │
│    temporal_nature: "RELATIVE_OFFSET"                                                  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 3. Specific Month / Year Milestone:                                                    │
│    raw_time_expression: "July 2016"                                                    │
│    coarse_value: "2016-07"                                                             │
│    temporal_nature: "EXACT_MONTH_YEAR"                                                 │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 4. Season / Cultural Event Anchor:                                                     │
│    raw_time_expression: "Holi 2020"                                                    │
│    coarse_value: "2020"                                                                │
│    temporal_nature: "SEASON_EVENT_BOUND"                                               │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

By retaining the `raw_time_expression`, natural approximations (e.g. *"around"*, *"approximately"*, *"maybe 2021"*) are preserved without inventing numerical confidence scores or probability distributions.

---

## 8. OCR Representation

The research evidence (Reddit Cases 5 & 6, Interview Ep 16 & 24) reveals a critical system breakdown: modern conversational AI search engines often treat literal text queries as conversational chatbot prompts, returning *"I can't help with that"* or searching for abstract themes instead of matching pixel text.

The V2 schema resolves this at the representation layer by explicitly isolating remembered printed text:

```json
// Example: Searching for an insurance bill by provider name (Reddit Case 5)
{
  "raw_input": "Progressive",
  "literal_text": ["Progressive"]
}
```

```json
// Example: Searching for a cryptocurrency order confirmation (Candidate 4, Ep 16)
{
  "raw_input": "bitcoin",
  "objects": [{ "name": "order confirmation" }],
  "literal_text": ["bitcoin"]
}
```

### Representation Boundary
- `literal_text` strictly represents **the user's memory of words printed on a surface**.
- It does **not** assert that a separate OCR microservice or technical index must be built.
- It simply ensures that the intelligence layer does not confuse a literal quote with a visual subject.

---

## 9. What Is Explicitly Excluded

In strict adherence to the audit in [part1_memory_schema_audit.md](file:///d:/graduation%20project%203/part1_memory_schema_audit.md), the following 12 capabilities are **explicitly excluded** from the V2 schema:

| Excluded Capability | Why Excluded (Audit Finding) | Evidence Status |
| :--- | :--- | :---: |
| **1. Dedicated Metaphorical Resemblance Subsystem** | Derived from literally **1 single episode** (Ep 15: octopus prop). Cannot justify a top-level subsystem. | HYPOTHESIS |
| **2. Explicit Negative Constraints** | Derived solely from post-task debrief reflections (Ep 02, Ep 07). Zero users ever entered a negative query. | PREMATURE |
| **3. Explicit "Forgotten Attributes" Tracking** | Users naturally omit what they do not recall; tracking a list of unremembered keys is an artificial construct. | PREMATURE |
| **4. Relational Graph Foreign Keys (`entity_id`, `actor_ref`)** | Over-engineering. Compositional nesting (`attributes` inside `objects`/`people`) represents all observed behavior simply. | PREMATURE |
| **5. Rigid Epistemic Confidence Enums (`CONFIRMED_FACT`, etc.)** | Speculative taxonomy. Users do not think or query in confidence categories. | PREMATURE |
| **6. Multi-Tier Event Hierarchy Ontologies** | Users search single terms (`wedding`, `haldi`). Deep multi-level tree structures are unsupported. | PREMATURE |
| **7. Separate Document Classification Subsystem** | Redundant. Documents behave like any other physical/digital entity in `objects` + `literal_text`. | REDUNDANT |
| **8. Separate Capture Modality Subsystem** | Inferred distinction between screenshots and camera photos; better represented as object types. | REDUNDANT |
| **9. Biometric Face ID Vector Tokens** | Internal system artifact. Fails completely for one-off contacts (watchmen, maids) who lack face clusters. | UNSUPPORTED |
| **10. Camera Hardware EXIF Metadata (ISO, Aperture)** | Zero evidence. Not a single user across 1,508 reviews and 25 interviews ever searched by camera specs. | UNSUPPORTED |
| **11. File System Paths and Formats (.jpg, folders)** | Zero evidence. Users do not recall life memories by directory structures or file extensions. | UNSUPPORTED |
| **12. Categorical Sentiment Polarity Scores** | Generic NLP construct (`positive: 0.85`). Does not reflect episodic memory recall. | UNSUPPORTED |

---

## 10. Evidence Boundaries

To ensure scientific integrity, the explicit boundaries of this representation schema must be recognized:

1. **Multilingual Generalization:**  
   The schema's linguistic grounding is based on English and Hindi-English code-mixing (Hinglish). While `raw_input` preserves any script, linguistic nuances of other language families (e.g., Romance, Semitic, or East Asian languages) were not tested in the empirical protocol.
2. **Video Temporal Granularity:**  
   The schema represents photo-level episodic memory. Intra-video temporal navigation (e.g. searching for a 5-second clip inside a 30-minute recording) is outside the scope of the underlying evidence.
3. **Collaborative / Shared Archive Semantics:**  
   The schema models personal memory for individual libraries. Multi-user shared libraries where photos belong to different participants were not evaluated.
4. **No Algorithmic Prescriptions:**  
   This document proves what information must be representable. It does **not** prove how that information should be indexed, matched, scored, or displayed. Those engineering decisions remain strictly for subsequent Discovery Engine architecture phases.
