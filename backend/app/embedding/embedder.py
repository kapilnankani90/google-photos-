"""
Local Embedding Service Module.

Provides CPU-based sentence-transformers embeddings matching the 384-dimensional
vector contract required by the PostgreSQL pgvector schema.
Governed by: part1_discovery_engine_implementation_spec.md (Sections 5.2, 9.1, 9.2, 23)

SPECIFICATION CONTRACT:
- Section 9.1 explicitly DISQUALIFIES 'all-MiniLM-L6-v2' (fails on Hinglish vernacular queries).
- Section 9.1 & 9.2 designate two approved 384-dimensional deployment benchmark candidates:
  1. Primary Initial Benchmark Candidate: 'intfloat/multilingual-e5-small'
  2. Fallback Contender: 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
- Model selection is NOT finalized in Step 3; it is an empirical benchmark decision in Step 5.
- Step 3 deploys with the initial candidate configurable via EMBEDDING_MODEL_NAME.
Zero external/paid APIs.
"""

from typing import List, Optional
import os
import threading
import logging
from sentence_transformers import SentenceTransformer

logger = logging.getLogger("LocalEmbedder")

SPEC_APPROVED_CANDIDATES = [
    "intfloat/multilingual-e5-small",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
]
INITIAL_BENCHMARK_CANDIDATE = "intfloat/multilingual-e5-small"
DISQUALIFIED_MODELS = [
    "all-MiniLM-L6-v2",
    "sentence-transformers/all-MiniLM-L6-v2",
]


class LocalEmbedder:
    """
    Singleton local text embedder using SentenceTransformer on CPU.
    Guarantees exact 384-dimensional vector outputs.
    Adheres strictly to the specification-approved benchmark candidates.
    """
    _instance: Optional["LocalEmbedder"] = None
    _lock = threading.Lock()

    def __init__(self, model_name: Optional[str] = None):
        # Resolve model name: explicit argument -> env var -> initial candidate
        resolved = (
            model_name
            or os.getenv("EMBEDDING_MODEL_NAME")
            or INITIAL_BENCHMARK_CANDIDATE
        ).strip()

        if resolved in DISQUALIFIED_MODELS:
            logger.warning(
                f"Model '{resolved}' is marked as DISQUALIFIED in spec Section 9.1 "
                f"(fails Hinglish vernacular queries). Defaulting to approved initial candidate '{INITIAL_BENCHMARK_CANDIDATE}'."
            )
            resolved = INITIAL_BENCHMARK_CANDIDATE

        self.model_name = resolved
        self.expected_dim = 384
        self._model: Optional[SentenceTransformer] = None
        self._init_lock = threading.Lock()

    @classmethod
    def get_instance(cls, model_name: Optional[str] = None) -> "LocalEmbedder":
        """Get or initialize singleton embedder instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(model_name=model_name)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (useful for test isolation)."""
        with cls._lock:
            cls._instance = None

    @property
    def model(self) -> SentenceTransformer:
        """Lazy loader for the SentenceTransformer model on CPU."""
        if self._model is None:
            with self._init_lock:
                if self._model is None:
                    # Explicitly run on CPU to meet zero-GPU deployment constraint
                    # Ensure offline loading is prioritized to avoid network drops
                    os.environ["HF_HUB_OFFLINE"] = "1"
                    os.environ["TRANSFORMERS_OFFLINE"] = "1"
                    try:
                        self._model = SentenceTransformer(
                            self.model_name, device="cpu", local_files_only=True
                        )
                    except Exception as err:
                        logger.info(f"Local offline load failed ({err}), attempting online fetch...")
                        os.environ.pop("HF_HUB_OFFLINE", None)
                        os.environ.pop("TRANSFORMERS_OFFLINE", None)
                        self._model = SentenceTransformer(self.model_name, device="cpu")
        return self._model

    def encode(self, text: str) -> List[float]:
        """
        Encode a single text passage into a 384-dimensional float vector.
        """
        if not text or not text.strip():
            # For empty passages, encode a space to produce a valid vector
            text = " "
        vec = self.model.encode(text, convert_to_numpy=True).tolist()
        if len(vec) != self.expected_dim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.expected_dim}, got {len(vec)} from model {self.model_name}"
            )
        return [float(x) for x in vec]

    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Encode a batch of text passages into 384-dimensional float vectors.
        """
        if not texts:
            return []
        cleaned = [t if (t and t.strip()) else " " for t in texts]
        vectors = self.model.encode(
            cleaned,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        results = []
        for vec in vectors:
            v_list = [float(x) for x in vec.tolist()]
            if len(v_list) != self.expected_dim:
                raise ValueError(
                    f"Embedding dimension mismatch: expected {self.expected_dim}, got {len(v_list)}"
                )
            results.append(v_list)
        return results
