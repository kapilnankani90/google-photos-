"""
Lightweight ASR Spelling and Hinglish Phonetic Normalization Layer.

Governed strictly by Memory Search Consistency Requirements:
- Normalizes obvious ASR phoneme and spelling errors in mixed Hinglish / Roman-script input.
- Does NOT translate Hinglish into Devanagari.
- Does NOT convert conversational queries into formal Hindi.
- Does NOT alter semantic meaning.
- Yields a canonical normalized representation used for consistent NLU extraction and cache indexing.
"""

import re
from typing import Dict

# Explicit word-boundary mapping for common ASR spelling errors and Hinglish phonetic variants
ASR_SPELLING_CORRECTIONS: Dict[str, str] = {
    # Wedding / Occasions
    "shadi": "shaadi",
    "shaadii": "shaadi",
    "weding": "wedding",
    "weeding": "wedding",
    "fnkton": "function",
    "fnction": "function",
    "funtion": "function",
    "fuction": "function",
    "bday": "birthday",
    "b'day": "birthday",
    "b-day": "birthday",

    # Objects / Vehicles / Media
    "baike": "bike",
    "byke": "bike",
    "fotu": "photo",
    "foto": "photo",
    "fotto": "photo",
    "phto": "photo",
    "phtoto": "photo",
    "poto": "photo",
    "camra": "camera",
    "camara": "camera",

    # People / Relations
    "bhaye": "bhai",
    "bhayi": "bhai",
    "famly": "family",
    "femily": "family",
    "fmly": "family",
    "famliy": "family",
    "frnds": "friends",
    "frends": "friends",
    "frnd": "friend",
    "frend": "friend",
    "dostn": "doston",
    "dostoon": "doston",

    # Places / Natural Elements
    "snset": "sunset",
    "sunst": "sunset",
    "snrise": "sunrise",
    "bech": "beach",
    "sumnder": "samundar",
    "samundr": "samundar",
    "pahad": "pahad",
    "rohtng": "rohtang",
    "mnali": "manali",
    "gwa": "goa",
}

# Compile case-insensitive word-boundary regexes
_CORRECTION_PATTERNS = [
    (re.compile(rf"\b{re.escape(misspelling)}\b", re.IGNORECASE), replacement)
    for misspelling, replacement in ASR_SPELLING_CORRECTIONS.items()
]


def normalize_memory_query(text: str) -> str:
    """
    Normalizes obvious ASR transcription errors and phonetic spellings in mixed Hinglish/Roman script.

    Examples:
        'shadi ka fnkton' -> 'shaadi ka function'
        'white baike' -> 'white bike'

    Preserves sentence structure, word meaning, and Roman script.
    """
    if not text:
        return ""

    cleaned = " ".join(text.split())
    for pattern, replacement in _CORRECTION_PATTERNS:
        cleaned = pattern.sub(replacement, cleaned)

    return " ".join(cleaned.split())


def get_cache_key(text: str) -> str:
    """
    Generates a canonical, case-folded, whitespace-normalized cache key
    from a user memory query.
    """
    normalized = normalize_memory_query(text or "")
    # Strip non-alphanumeric punctuation for resilient cache matching
    canonical = re.sub(r"[^\w\s]", "", normalized.lower())
    return " ".join(canonical.split())
