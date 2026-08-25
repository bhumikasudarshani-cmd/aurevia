"""
NLP model abstraction for the Aurevia NLP pipeline.

Defines the interface and a DEMO_MODE implementation.
Real transformer-based models can be plugged in without
changing the public API.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict
from app.core.logging import logger


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class NLPModelResult:
    """Structured output from an NLP model."""
    model_name: str
    model_version: str
    mode: str                          # "demo" | "production"
    indicators: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class BaseNLPModel(ABC):
    """Abstract NLP model interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Model name identifier."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Model version string."""
        ...

    @abstractmethod
    def analyze(self, text: str, tokens: list[str]) -> NLPModelResult:
        """
        Run NLP analysis on the preprocessed text and tokens.

        Args:
            text:   Preprocessed/normalized text.
            tokens: Tokens produced by the tokenizer.

        Returns:
            NLPModelResult with indicators and metadata.
        """
        ...


# ---------------------------------------------------------------------------
# Demo implementation (no ML dependencies)
# ---------------------------------------------------------------------------

class DemoNLPModel(BaseNLPModel):
    """
    DEMO_MODE NLP model.

    Returns deterministic, plausible-looking output without requiring
    any model downloads or GPU.  Clearly marked as demo output.
    """

    _NAME = "aurevia-demo-nlp"
    _VERSION = "0.1.0-demo"

    @property
    def name(self) -> str:
        return self._NAME

    @property
    def version(self) -> str:
        return self._VERSION

    def analyze(self, text: str, tokens: list[str]) -> NLPModelResult:
        """
        Produce deterministic demo NLP indicators.

        Indicators are computed from basic text statistics only —
        no actual ML inference is performed.
        """
        word_count = len(tokens)
        avg_token_length = (
            sum(len(t) for t in tokens) / word_count if word_count else 0.0
        )

        indicators: Dict[str, Any] = {
            "token_count": word_count,
            "avg_token_length": round(avg_token_length, 2),
            "is_demo": True,
            "note": (
                "DEMO_MODE active. Indicators are derived from basic "
                "text statistics, not real model inference."
            ),
        }

        logger.debug(
            "DemoNLPModel.analyze complete: token_count=%d", word_count
        )

        return NLPModelResult(
            model_name=self._NAME,
            model_version=self._VERSION,
            mode="demo",
            indicators=indicators,
        )


# ---------------------------------------------------------------------------
# Module-level default instance
# ---------------------------------------------------------------------------

_default_model: BaseNLPModel = DemoNLPModel()


def get_nlp_model() -> BaseNLPModel:
    """Return the active NLP model."""
    return _default_model
