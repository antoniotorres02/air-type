"""
Módulo para transcripción de audio usando la API de Groq
"""
import requests
import json
import numpy as np
import pyautogui
from io import BytesIO
from scipy.io.wavfile import write as write_wav
import pyperclip


# Configuración de transcripción
groq_api_key = ""
model_name = ""

def setup_transcription(config):
    """Configura el servicio de transcripción con los parámetros proporcionados"""
    global groq_api_key, model_name
    groq_api_key = config["groq_api_key"]
    model_name = config["model_name"]

def transcribe_with_groq(audio_data, sample_rate):
    """Transcribe el audio utilizando la API de Groq"""
    if audio_data is None:
        return ""

    print("Convirtiendo audio a formato WAV...")
    wav_io = BytesIO()
    audio_int16 = np.int16(audio_data * 32767)
    write_wav(wav_io, sample_rate, audio_int16)
    wav_io.seek(0)
    print("Audio convertido.")

    headers = {
        "Authorization": f"Bearer {groq_api_key}",
    }

    files = {
        'file': ('audio.wav', wav_io, 'audio/wav')
    }
    data = {
        'model': model_name,
    }

    print(f"Enviando audio a Groq API (modelo: {model_name})...")
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

def write_text(text):
    """Escribe el texto transcrito usando pyperclip y pyautogui"""
    if text:
        print("Escribiendo texto...")
        pyperclip.copy(text)  # Copia el texto al portapapeles
        pyautogui.hotkey('ctrl', 'v')  # Pega el texto usando el atajo de teclado
        print("Texto escrito.")
    else:
        print("No hay texto para escribir.")