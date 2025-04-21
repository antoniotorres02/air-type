"""
API pública del módulo de transcripción.
"""
from .factory import setup_transcription, get_transcriber
from .utils import write_text

__all__ = ['setup_transcription', 'get_transcriber', 'write_text']