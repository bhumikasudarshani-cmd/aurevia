"""
Transcription abstraction.

Defines the interface for speech-to-text providers.
Phase 3 provides only the interface and a demo stub.

A real implementation (Whisper, Google STT, etc.) can be introduced
in a later phase without changing the public API.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from app.core.logging import logger


@dataclass
class TranscriptionResult:
    """Result from a transcription provider."""
    available: bool
    text: Optional[str]
    provider: Optional[str]


class BaseTranscriptionProvider(ABC):
    """Abstract interface for speech-to-text providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def transcribe(self, data: bytes, fmt: str, sample_rate: int) -> TranscriptionResult:
        """
        Transcribe audio bytes to text.

        Args:
            data:        Raw audio bytes.
            fmt:         Audio format string.
            sample_rate: Sample rate in Hz.

        Returns:
            TranscriptionResult.
        """
        ...


class DemoTranscriptionProvider(BaseTranscriptionProvider):
    """
    Demo/placeholder transcription provider.

    Always returns available=False indicating transcription is not
    yet implemented. This allows the API to include the transcription
    field without blocking Phase 3.
    """

    @property
    def name(self) -> str:
        return "demo-transcription-stub"

    def transcribe(self, data: bytes, fmt: str, sample_rate: int) -> TranscriptionResult:
        logger.debug("DemoTranscriptionProvider: transcription not available in Phase 3")
        return TranscriptionResult(
            available=False,
            text=None,
            provider=self.name,
        )


_default_provider: BaseTranscriptionProvider = DemoTranscriptionProvider()


def get_transcription_provider() -> BaseTranscriptionProvider:
    """Return the active transcription provider."""
    return _default_provider
