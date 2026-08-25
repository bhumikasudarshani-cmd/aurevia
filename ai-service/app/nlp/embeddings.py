"""
Embeddings abstraction for the Aurevia NLP pipeline.

Defines the interface and a DEMO_MODE implementation that produces
deterministic placeholder vectors without any model downloads.

A real Sentence Transformer provider can be introduced later without
changing the public API.
"""

import hashlib
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from app.core.logging import logger


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class EmbeddingResult:
    """Result from an embedding provider."""
    provider: str
    dimensions: int
    vector: List[float]
    is_demo: bool


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class BaseEmbeddingProvider(ABC):
    """Abstract embedding provider interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        ...

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Embedding vector size."""
        ...

    @abstractmethod
    def embed(self, text: str) -> EmbeddingResult:
        """
        Produce an embedding vector for the given text.

        Args:
            text: Preprocessed text to embed.

        Returns:
            EmbeddingResult with vector and metadata.
        """
        ...


# ---------------------------------------------------------------------------
# Demo implementation (no ML dependencies, fully deterministic)
# ---------------------------------------------------------------------------

_DEMO_DIMENSIONS = 64  # Small but illustrative


class DemoEmbeddingProvider(BaseEmbeddingProvider):
    """
    DEMO_MODE embedding provider.

    Produces a deterministic, hash-derived pseudo-embedding vector.
    Vectors are reproducible for the same input text.

    Clearly marked as demo — NOT suitable for semantic similarity.
    Replace with SentenceTransformers in a later phase.
    """

    _NAME = "aurevia-demo-embeddings"

    @property
    def name(self) -> str:
        return self._NAME

    @property
    def dimensions(self) -> int:
        return _DEMO_DIMENSIONS

    def embed(self, text: str) -> EmbeddingResult:
        """
        Produce a deterministic demo embedding.

        Uses SHA-256 of the input to seed a normalized pseudo-random vector.
        Guaranteed reproducible for the same input.

        Args:
            text: Input text.

        Returns:
            EmbeddingResult.
        """
        vector = self._hash_to_vector(text)
        logger.debug(
            "DemoEmbeddingProvider.embed: dims=%d is_demo=True", self.dimensions
        )
        return EmbeddingResult(
            provider=self._NAME,
            dimensions=self.dimensions,
            vector=vector,
            is_demo=True,
        )

    def _hash_to_vector(self, text: str) -> List[float]:
        """
        Derive a stable, normalised float vector from text via SHA-256.

        Each 4 bytes of the hash seed one float component in [-1, 1].
        The process cycles over the hash bytes to fill all dimensions.
        """
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        vector: List[float] = []
        digest_len = len(digest)

        for i in range(self.dimensions):
            # Use 4 bytes per component, cycling through digest
            start = (i * 4) % (digest_len - 3)
            raw = int.from_bytes(digest[start : start + 4], byteorder="big", signed=True)
            # Normalize to [-1.0, 1.0]
            normalized = raw / (2**31)
            vector.append(round(normalized, 6))

        return vector


# ---------------------------------------------------------------------------
# Module-level default instance
# ---------------------------------------------------------------------------

_default_provider: BaseEmbeddingProvider = DemoEmbeddingProvider()


def get_embedding_provider() -> BaseEmbeddingProvider:
    """Return the active embedding provider."""
    return _default_provider


def embed(text: str) -> EmbeddingResult:
    """
    Convenience function: embed text using the active provider.

    Args:
        text: Preprocessed text.

    Returns:
        EmbeddingResult.
    """
    return _default_provider.embed(text)
