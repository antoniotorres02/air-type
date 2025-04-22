"""
API pública del módulo de transcripción.
"""
from .factory import setup_transcription, get_transcriber
from .utils import write_text, save_active_window
from .bubble import bubble_manager, BubbleManager


__all__ = ['setup_transcription', 'get_transcriber', 'write_text', 'bubble_manager', 'BubbleManager', save_active_window]