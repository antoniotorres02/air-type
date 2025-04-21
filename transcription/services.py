import numpy as np
from io import BytesIO
from scipy.io.wavfile import write as write_wav
import requests
import json



class GroqTranscriptionService:
    """Implementación de transcripción usando la API de Groq."""

    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name

    def transcribe(self, audio_data: np.ndarray, sample_rate: int) -> str:
        """Transcribe el audio utilizando la API de Groq."""
        if audio_data is None:
            return ""

        print("Convirtiendo audio a formato WAV...")
        wav_io = BytesIO()
        audio_int16 = np.int16(audio_data * 32767)
        write_wav(wav_io, sample_rate, audio_int16)
        wav_io.seek(0)
        print("Audio convertido.")

        headers = {"Authorization": f"Bearer {self.api_key}"}
        files = {'file': ('audio.wav', wav_io, 'audio/wav')}
        data = {'model': self.model_name}

        print(f"Enviando audio a Groq API (modelo: {self.model_name})...")
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers=headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            result = response.json()
            transcribed_text = result.get("text", "")
            print("Transcripción recibida.")
            return transcribed_text
        except requests.exceptions.RequestException as e:
            print(f"Error de red o HTTP al contactar la API Groq: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    print(f"Respuesta de la API: {e.response.status_code} - {e.response.text}")
                except json.JSONDecodeError:
                    print(f"Respuesta de la API (no JSON): {e.response.status_code} - {e.response.text}")
            return ""
        except Exception as e:
            print(f"Error inesperado durante la transcripción con Groq: {e}")
            return ""
