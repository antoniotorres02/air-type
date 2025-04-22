"""
Factory y gestor Singleton para servicios de transcripción.
"""
from typing import Dict, Any, Optional
from .services import GroqTranscriptionService
from .interfaces import TranscriptionService

import os 

_transcription_instance: Optional[TranscriptionService] = None

def setup_transcription(config: Dict[str, Any]) -> TranscriptionService:
    """Crea o devuelve la instancia singleton del servicio."""
    global _transcription_instance
    
    if _transcription_instance is None:
        provider = config.get("provider", "groq")
        
        if provider == "groq":
            _transcription_instance = GroqTranscriptionService(
                api_key=os.getenv("GROQ_API_KEY", ""),
                model_name=os.getenv("MODEL_NAME", "")
            )
        else:
            raise ValueError(f"Proveedor no soportado: {provider}")
    
    return _transcription_instance

def get_transcriber() -> TranscriptionService:
    """Obtiene la instancia singleton del transcriptor."""
    if _transcription_instance is None:
        raise RuntimeError("Transcriptor no inicializado. Llama primero a setup_transcription()")
    return _transcription_instance