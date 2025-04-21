"""
Definición de interfaces para servicios de transcripción.
"""
from typing import Protocol, runtime_checkable
import numpy as np

@runtime_checkable
class TranscriptionService(Protocol):
    """Interfaz base para servicios de transcripción."""

    def transcribe(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Transcribe audio a texto."""
        ...