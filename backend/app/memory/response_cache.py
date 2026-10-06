"""
D2 Memory Search Full Response Cache and Deterministic Ordering Layer.

Governed strictly by Memory Search Consistency Requirements:
- Caches the COMPLETE D2 MemorySearchResponse based on canonical normalized query key.
- Resolves phonetic / ASR variations (e.g. 'fnkton' vs 'function', 'baike' vs 'bike') to the same canonical key.
- Does NOT collapse genuinely different queries.
- Preserves the user's verbatim input query in original_memory_text and raw_input.
- Implements deterministic candidate ordering with stable tie-breaking on equal relevance scores.
"""

import copy
import logging
from typing import Dict, List, Optional, Tuple, Any

from app.memory.schemas import MemorySearchResponse, MemoryInterpretationResponse
from app.memory.normalization import get_cache_key
from app.retrieval.models import CandidateResult

logger = logging.getLogger("MemoryResponseCache")

# In-memory full response caches for D2 endpoints
_FULL_SEARCH_CACHE: Dict[str, MemorySearchResponse] = {}
_INTERPRETATION_RESPONSE_CACHE: Dict[str, MemoryInterpretationResponse] = {}


def make_search_cache_key(raw_input: str, top_k: int = 8, enable_recovery: bool = True) -> str:
    """
    Constructs a canonical cache key based on the normalized memory query,
    retrieval top_k parameter, and recovery toggle.
    """
    normalized_key = get_cache_key(raw_input or "")
    return f"{normalized_key}__k{top_k}__rec{int(enable_recovery)}"


def make_interpretation_cache_key(raw_input: str) -> str:
    """Constructs a canonical cache key for interpretation-only endpoint."""
    return get_cache_key(raw_input or "")


def get_cached_search_response(
    raw_input: str,
    top_k: int = 8,
    enable_recovery: bool = True,
) -> Optional[MemorySearchResponse]:
    """
    Retrieves cached MemorySearchResponse for an identical normalized query.
    Preserves the caller's verbatim original_memory_text and raw_input on the returned clone.
    """
    key = make_search_cache_key(raw_input, top_k, enable_recovery)
    if key not in _FULL_SEARCH_CACHE:
        return None

    cached_item = _FULL_SEARCH_CACHE[key]
    cloned = cached_item.model_copy(deep=True)

    # Preserve user's verbatim query authoritatively
    cloned.original_memory_text = raw_input
    cloned.raw_input = raw_input
    cloned.structured_clues.original_memory_text = raw_input
    if isinstance(cloned.v2_frame, dict):
        cloned.v2_frame["raw_input"] = raw_input
    elif hasattr(cloned.v2_frame, "raw_input"):
        cloned.v2_frame.raw_input = raw_input

    logger.info("D2 full search response cache hit for key: %s", key)
    return cloned


def cache_search_response(
    raw_input: str,
    response: MemorySearchResponse,
    top_k: int = 8,
    enable_recovery: bool = True,
) -> None:
    """Stores a deep copy of the complete MemorySearchResponse in the cache."""
    key = make_search_cache_key(raw_input, top_k, enable_recovery)
    _FULL_SEARCH_CACHE[key] = response.model_copy(deep=True)


def get_cached_interpretation_response(raw_input: str) -> Optional[MemoryInterpretationResponse]:
    """Retrieves cached MemoryInterpretationResponse for interpretation endpoint."""
    key = make_interpretation_cache_key(raw_input)
    if key not in _INTERPRETATION_RESPONSE_CACHE:
        return None

    cached_item = _INTERPRETATION_RESPONSE_CACHE[key]
    cloned = cached_item.model_copy(deep=True)
    cloned.original_memory_text = raw_input
    cloned.structured_clues.original_memory_text = raw_input
    if hasattr(cloned.v2_representation, "raw_input"):
        cloned.v2_representation.raw_input = raw_input
    return cloned


def cache_interpretation_response(raw_input: str, response: MemoryInterpretationResponse) -> None:
    """Stores a deep copy of MemoryInterpretationResponse in the cache."""
    key = make_interpretation_cache_key(raw_input)
    _INTERPRETATION_RESPONSE_CACHE[key] = response.model_copy(deep=True)


def make_deterministic_candidate_ordering(results: List[CandidateResult]) -> List[CandidateResult]:
    """
    Sorts candidate results with stable, auditable tie-breaking:
    1. Primary: Score descending (-round(score, 6))
    2. Secondary: Stable candidate/chunk UUID (lexicographical)
    3. Tertiary: Content string (lexicographical)

    Re-indexes 1-indexed ranks deterministically.
    """
    if not results:
        return []

    def tie_breaker_key(c: CandidateResult) -> Tuple[float, str, str]:
        score_val = -round(float(c.score), 6)
        id_val = str(c.chunk_id or c.candidate_id or "")
        content_val = str(c.content or "")
        return (score_val, id_val, content_val)

    sorted_results = sorted(results, key=tie_breaker_key)
    for idx, c in enumerate(sorted_results, start=1):
        c.rank = idx
    return sorted_results


def clear_all_memory_caches() -> None:
    """Clears all D2 search and interpretation response caches."""
    _FULL_SEARCH_CACHE.clear()
    _INTERPRETATION_RESPONSE_CACHE.clear()


def get_memory_cache_stats() -> Dict[str, int]:
    """Returns diagnostic statistics for D2 memory caches."""
    return {
        "search_cache_count": len(_FULL_SEARCH_CACHE),
        "interpretation_cache_count": len(_INTERPRETATION_RESPONSE_CACHE),
    }
