"""
Deterministic Rule-Based Memory Interpretation Layer.

Governed strictly by:
- part1_discovery_engine_implementation_spec.md (Sections 7.2, 8.2, 23)
- part1_memory_representation_schema_v2.md
- part1_discovery_engine_operating_spec_final.md (Canonical Traces 1–8)

Implements:
1. Input sanitization while strictly preserving verbatim raw_input
2. Hinglish / vernacular particle identification and normalization
3. Deterministic extraction of:
   - Temporal concepts (coarse era, relative offset, exact month-year, season/event)
   - People & kinship concepts (roles, counts, bound attributes, possessives)
   - Object concepts (physical props, documents, bound visual attributes, possessives)
   - Action concepts (physical verbs, sports, bodily poses)
   - Milestone event concepts (event_name, sub_event)
   - Spatial settings (geographic landscapes, architectural boundaries)
   - Literal text / OCR targets (quoted strings, standalone brand/document names)
4. Ambiguity / open-domain classification to govern Gemini fallback routing
5. Strict non-fabrication guarantee (never populates unmentioned details)
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from app.representation.models import (
    PersonConcept,
    EventConcept,
    ObjectConcept,
    TemporalConcept,
    V2MemoryRepresentation,
)

# =============================================================================
# VERNACULAR & HINGLISH PARTICLES (Section 8.2 & 23)
# =============================================================================

# Known Hindi / Hinglish grammatical particles and search boilerplate
VERNACULAR_PARTICLES = {
    "ki", "ke", "ka", "wali", "wala", "wale", "se", "mein", "main", "ko",
    "pe", "par", "ke sath", "ke saath", "k sath", "hai", "tha", "thi",
    "photo", "photos", "pic", "pics", "picture", "pictures", "image", "images",
}

# Number word mapping for cardinality extraction
WORD_TO_NUMBER = {
    "one": 1, "ek": 1,
    "two": 2, "do": 2,
    "three": 3, "teen": 3,
    "four": 4, "chaar": 4,
    "five": 5, "paanch": 5,
    "six": 6, "che": 6,
    "seven": 7, "saat": 7,
    "eight": 8, "aath": 8,
    "nine": 9, "nau": 9,
    "ten": 10, "das": 10,
}

# Canonical kinship and social roles (Section 5.2)
KINSHIP_ROLES = {
    "sister": "sister", "sisters": "sister",
    "brother": "brother", "brothers": "brother",
    "cousin": "cousin", "cousins": "cousin",
    "maid": "maid",
    "watchman": "watchman",
    "colleague": "colleague", "colleagues": "colleague",
    "friend": "friend", "friends": "friend",
    "lady": "lady", "ladies": "lady",
    "family": "family",
    "nephew": "nephew",
    "grandchild": "grandchild", "grandchildren": "grandchild",
    "grandmother": "grandmother", "dadi": "grandmother", "nani": "grandmother",
    "grandfather": "grandfather", "dada": "grandfather", "nana": "grandfather",
    "mother": "mother", "mom": "mother", "maa": "mother",
    "father": "father", "dad": "father", "papa": "father",
}

# Salient objects & props (Section 5.4)
OBJECT_VOCABULARY = {
    "bike": "bike", "bicycle": "bike", "motorcycle": "bike",
    "cake": "cake",
    "papaya": "papaya",
    "ring box": "ring box",
    "diya": "diya",
    "truck": "truck",
    "document": "document", "documents": "document",
    "boarding pass": "boarding pass",
    "ice": "ice",
    "car": "car",
    "fan": "cooling fan", "cooling fan": "cooling fan",
    "order confirmation": "order confirmation",
    "flower": "flower", "flowers": "flower",
    "passport": "passport",
    "laptop": "laptop",
    "bill": "bill", "invoice": "invoice",
}

# Milestone events & celebrations (Section 5.3)
EVENT_VOCABULARY = {
    "wedding": ("wedding", None),
    "haldi": ("wedding", "haldi"),
    "rehearsal": ("wedding", "rehearsal"),
    "diwali": ("diwali", None),
    "deepavali": ("diwali", None),
    "birthday": ("birthday", None),
    "holi": ("holi", None),
    "farewell lunch": ("farewell", "farewell lunch"),
    "farewell": ("farewell", None),
    "engagement": ("engagement", None),
    "college trip": ("college trip", None),
    "convocation": ("convocation", None),
    "anniversary": ("anniversary", None),
}

# Spatial settings (Section 5.8)
SPATIAL_VOCABULARY = {
    "rohtang": "rohtang",
    "mussoorie": "Mussoorie",
    "malwan": "malwan",
    "beach": "beach",
    "gate": "gate",
    "mountain": "mountain",
    "snowy mountain": "snowy mountain",
    "snow mountain": "mountain",
    "airport": "airport",
    "temple": "temple",
    "office": "office",
    "college": "college",
    "lake": "lake",
    "park": "park",
    "garden": "garden",
}

# Visual attributes (colors, attire)
COLOR_ATTRIBUTES = {
    "white", "yellow", "blue", "black", "red", "green", "pink", "purple", "orange",
}

# Known literal text targets (e.g. from canonical cases / OCR queries)
LITERAL_OCR_TARGETS = {
    "progressive", "bitcoin", "i love being a man",
}


def sanitize_input(text: str) -> str:
    """Sanitizes user input by normalizing whitespace without modifying characters."""
    if not text:
        return ""
    return " ".join(text.strip().split())


def strip_vernacular_particles(text: str) -> str:
    """
    Strips grammatical code-mixed particles (Hinglish ki, wali, etc.)
    and search stopwords (photo, pic) from a copy of the text for semantic lookup.
    The original raw_input remains untouched.
    """
    tokens = text.split()
    cleaned = []
    i = 0
    while i < len(tokens):
        # Multi-word particle check (e.g., 'ke sath', 'ke saath')
        if i + 1 < len(tokens):
            two_word = f"{tokens[i]} {tokens[i+1]}".lower()
            if two_word in VERNACULAR_PARTICLES:
                i += 2
                continue
        lower_token = tokens[i].lower()
        if lower_token in VERNACULAR_PARTICLES:
            i += 1
            continue
        cleaned.append(tokens[i])
        i += 1
    return " ".join(cleaned)


# =============================================================================
# DETERMINISTIC EXTRACTION LOGIC
# =============================================================================

def extract_literal_text(text: str) -> List[str]:
    """
    Extracts explicit OCR print text snippets:
    - Text enclosed in double or single quotes
    - Known literal OCR targets (e.g., 'Progressive', 'bitcoin')
    """
    literal = []
    # 1. Quoted text
    quotes = re.findall(r'["\']([^"\']+)["\']', text)
    for q in quotes:
        cleaned_q = q.strip()
        if cleaned_q and cleaned_q not in literal:
            literal.append(cleaned_q)

    # 2. Known standalone OCR terms if not already found in quotes
    lower = text.strip().lower()
    if lower in LITERAL_OCR_TARGETS and text.strip() not in literal:
        # Preserve original capitalization
        literal.append(text.strip())

    return literal


def extract_temporal(text: str) -> Optional[TemporalConcept]:
    """
    Extracts temporal anchors adhering to the 4 spec-defined temporal natures:
    1. EXACT_MONTH_YEAR (e.g., 'July 2016', 'oct 2020')
    2. COARSE_YEAR_ERA (e.g., '2021', '2016')
    3. RELATIVE_OFFSET (e.g., 'around 4 years ago', '4 years ago')
    4. SEASON_EVENT_BOUND (e.g., 'Holi 2020', 'summer 2019')
    """
    lower = text.lower()

    # 1. EXACT_MONTH_YEAR: e.g. "July 2016", "in August 2021"
    month_regex = r'\b(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\s+(\d{4})\b'
    match_month = re.search(month_regex, lower)
    if match_month:
        month_name = match_month.group(1).capitalize()
        year = match_month.group(2)
        raw_expr = match_month.group(0)
        # Standardize month number
        month_map = {
            "jan": "01", "january": "01", "feb": "02", "february": "02",
            "mar": "03", "march": "03", "apr": "04", "april": "04",
            "may": "05", "jun": "06", "june": "06", "jul": "07", "july": "07",
            "aug": "08", "august": "08", "sep": "09", "september": "09",
            "oct": "10", "october": "10", "nov": "11", "november": "11",
            "dec": "12", "december": "12"
        }
        m_num = month_map.get(month_name.lower(), "01")
        return TemporalConcept(
            raw_time_expression=raw_expr,
            coarse_value=f"{year}-{m_num}",
            temporal_nature="EXACT_MONTH_YEAR",
        )

    # 2. RELATIVE_OFFSET: e.g. "around 4 years ago", "4 years ago", "2 months back", "last year"
    rel_regex = r'\b((?:around|about|approximately|maybe)?\s*\d+\s*(?:years?|months?)\s*(?:ago|back|pehle))\b'
    match_rel = re.search(rel_regex, lower)
    if match_rel:
        raw_expr = match_rel.group(1).strip()
        # Coarse value strips approximation prefix
        coarse = re.sub(r'^(?:around|about|approximately|maybe)\s*', '', raw_expr).strip()
        return TemporalConcept(
            raw_time_expression=raw_expr,
            coarse_value=coarse,
            temporal_nature="RELATIVE_OFFSET",
        )

    # 3. SEASON_EVENT_BOUND: e.g. "Holi 2020", "Diwali 2019", "summer 2021"
    season_regex = r'\b(holi|diwali|summer|winter|monsoon|spring)\s+(\d{4})\b'
    match_season = re.search(season_regex, lower)
    if match_season:
        raw_expr = match_season.group(0)
        year = match_season.group(2)
        return TemporalConcept(
            raw_time_expression=raw_expr,
            coarse_value=year,
            temporal_nature="SEASON_EVENT_BOUND",
        )

    # 4. COARSE_YEAR_ERA: standalone 4-digit year (1990 - 2030)
    year_regex = r'\b(19\d{2}|20[0-2]\d)\b'
    match_year = re.search(year_regex, lower)
    if match_year:
        year = match_year.group(1)
        return TemporalConcept(
            raw_time_expression=year,
            coarse_value=year,
            temporal_nature="COARSE_YEAR_ERA",
        )

    return None


def extract_events(text: str) -> Optional[EventConcept]:
    """Extracts milestone events and sub-events."""
    lower = text.lower()
    # Check multi-word events first
    for ev_key, (name, sub) in sorted(EVENT_VOCABULARY.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r'\b' + re.escape(ev_key) + r'\b'
        if re.search(pattern, lower):
            # Check if there is an explicit sub-event mentioned elsewhere in text
            if sub is None:
                if "haldi" in lower:
                    sub = "haldi"
                elif "rehearsal" in lower:
                    sub = "rehearsal"
                elif "farewell lunch" in lower:
                    sub = "farewell lunch"
            return EventConcept(event_name=name, sub_event=sub)
    return None


def extract_people(text: str) -> List[PersonConcept]:
    """
    Extracts people concepts:
    - Kinship / social role
    - Count / cardinality (e.g. '5 sisters', 'two ladies')
    - Possessive (e.g. 'my cousin', 'meri maid', 'our friends')
    - Bound visual attributes (e.g. 'yellow suit', 'blue outfit')
    """
    people: List[PersonConcept] = []
    lower = text.lower()

    # Look for possessive markers
    possessive = None
    if re.search(r'\b(my|meri|mere)\b', lower):
        possessive = "my"
    elif re.search(r'\b(our|hamara|hamare)\b', lower):
        possessive = "our"

    # Search for role mentions
    for surface_role, canonical_role in KINSHIP_ROLES.items():
        # Match word boundary
        pattern = r'(?:(\d+|one|two|three|four|five|six|seven|eight|nine|ten|ek|do|teen|chaar|paanch)\s+)?\b' + re.escape(surface_role) + r'\b'
        match = re.search(pattern, lower)
        if match:
            # Determine count
            count = None
            count_str = match.group(1)
            if count_str:
                if count_str.isdigit():
                    count = int(count_str)
                elif count_str in WORD_TO_NUMBER:
                    count = WORD_TO_NUMBER[count_str]

            # Look for bound attributes near the person (e.g. "in yellow suit", "wearing blue outfit", "yellow suit")
            attributes = []
            for col in COLOR_ATTRIBUTES:
                attr_pattern = rf'\b(?:in|with|wearing)?\s*({col}\s+(?:suit|outfit|dress|shirt|saree|kurta|t-shirt))\b'
                attr_match = re.search(attr_pattern, lower)
                if attr_match:
                    matched_attr = attr_match.group(1).strip()
                    if matched_attr not in attributes:
                        attributes.append(matched_attr)
                elif f"family in {col}" in lower or f"family {col}" in lower:
                    if col not in attributes:
                        attributes.append(col)

            # Check if this person role is already added
            existing = [p for p in people if p.role == canonical_role]
            if not existing:
                people.append(PersonConcept(
                    role=canonical_role,
                    count=count,
                    attributes=attributes,
                    possessive=possessive,
                ))

    return people


def extract_objects(text: str) -> List[ObjectConcept]:
    """
    Extracts physical objects, vehicles, props, and documents:
    - Name
    - Bound visual modifiers (e.g., 'white' for bike, 'yellow' for truck)
    - Possessive (e.g., 'my')
    """
    objects: List[ObjectConcept] = []
    lower = text.lower()

    # Look for possessive markers
    possessive = None
    if re.search(r'\b(my|meri|mere)\b', lower):
        possessive = "my"
    elif re.search(r'\b(our|hamara|hamare)\b', lower):
        possessive = "our"

    # Search for object items
    for obj_surface, canonical_name in sorted(OBJECT_VOCABULARY.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r'\b' + re.escape(obj_surface) + r'\b'
        if re.search(pattern, lower):
            # Check for bound visual attributes (e.g. "white bike", "yellow truck", "steel plate")
            attributes = []
            for col in COLOR_ATTRIBUTES:
                col_pattern = rf'\b{col}\s+{re.escape(obj_surface)}\b'
                if re.search(col_pattern, lower):
                    attributes.append(col)
            if "steel plate" in lower and canonical_name == "cake":
                attributes.append("steel plate")

            # Avoid duplicate canonical names
            if not any(o.name == canonical_name for o in objects):
                objects.append(ObjectConcept(
                    name=canonical_name,
                    attributes=attributes,
                    possessive=possessive,
                ))

    return objects


def extract_actions(text: str) -> List[str]:
    """Extracts dynamic activities, physical actions, and poses."""
    actions = []
    lower = text.lower()

    action_patterns = [
        (r'\b(?:rafting)\b', "rafting"),
        (r'\b(?:skiing|sking)\b', "skiing"),
        (r'\b(?:lighting(?:\s+a)?\s+diya|diya\s+lighting)\b', "lighting diya"),
        (r'\b(?:peeling\s+papaya)\b', "peeling papaya"),
        (r'\b(?:arms\s+crossed|crossed\s+arms)\b', "arms crossed"),
        (r'\b(?:holding\s+(?:the\s+)?ring\s+box)\b', "holding the ring box"),
        (r'\b(?:firecracker\s+lighted)\b', "firecracker lighted"),
    ]

    for pat, action_name in action_patterns:
        if re.search(pat, lower):
            if action_name not in actions:
                actions.append(action_name)

    return actions


def extract_spatial_setting(text: str) -> Optional[str]:
    """
    Extracts broad geographic destination or architectural boundary.
    Handles prepositional cues ('at the gate', 'near snowy mountain', 'rohtang ki...').
    """
    lower = text.lower()
    for setting_key, canonical_setting in sorted(SPATIAL_VOCABULARY.items(), key=lambda x: len(x[0]), reverse=True):
        pattern = r'\b' + re.escape(setting_key) + r'\b'
        if re.search(pattern, lower):
            return canonical_setting
    return None


def is_ambiguous_query(
    text: str,
    parsed: V2MemoryRepresentation
) -> bool:
    """
    Determines whether a query requires Gemini structured fallback parsing.

    A query is considered DETERMINISTIC (does not need Gemini) if:
    - It matches one of the canonical patterns (e.g. 5 sisters, white bike, Progressive, etc.)
    - It has cleanly extracted non-empty core structures (e.g. people, objects, events, or literal_text)

    A query is considered AMBIGUOUS / OPEN-DOMAIN if:
    - It is a long, conversational, or multi-clause sentence where NO structured fields
      could be extracted deterministically, or where intent cannot be pinned down.
    - E.g. "I think there was a snapshot where we were all sitting around looking surprised at something"
    """
    # If the user has extracted any substantive frame components:
    has_substantive = bool(
        parsed.people or
        parsed.events or
        parsed.objects or
        parsed.actions or
        parsed.literal_text or
        (parsed.temporal and parsed.spatial_setting)
    )

    if has_substantive:
        return False

    # If it's a very short query (<= 3 words) that matches pure noise or completely unknown terms,
    # or a long conversational sentence without any extracted signals:
    words = text.strip().split()
    if len(words) >= 4 and not has_substantive:
        return True

    return False


def parse_deterministically(raw_input: str) -> V2MemoryRepresentation:
    """
    Executes the deterministic interpretation layer for any natural-language input.
    Guarantees strict schema adherence and verbatim preservation of raw_input.
    """
    sanitized = sanitize_input(raw_input)
    if not sanitized:
        return V2MemoryRepresentation(raw_input=raw_input)

    # 1. Literal OCR Text
    literal_text = extract_literal_text(sanitized)

    # If the query is an exact match for a single literal OCR token (e.g., "Progressive"),
    # avoid spurious entity matches.
    if len(literal_text) == 1 and sanitized.lower() == literal_text[0].lower():
        return V2MemoryRepresentation(
            raw_input=raw_input,
            literal_text=literal_text,
        )

    # 2. Temporal
    temporal = extract_temporal(sanitized)

    # 3. Events
    events = extract_events(sanitized)

    # 4. People
    people = extract_people(sanitized)

    # 5. Objects
    objects = extract_objects(sanitized)

    # 6. Actions
    actions = extract_actions(sanitized)

    # 7. Spatial Setting
    spatial = extract_spatial_setting(sanitized)

    return V2MemoryRepresentation(
        raw_input=raw_input,
        people=people,
        events=events,
        objects=objects,
        actions=actions,
        temporal=temporal,
        literal_text=literal_text,
        spatial_setting=spatial,
    )
