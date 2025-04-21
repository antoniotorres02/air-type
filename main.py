import sounddevice as sd
import numpy as np
import requests
import pyautogui
import threading
import json
import tkinter as tk
from pynput import keyboard
from io import BytesIO
from scipy.io.wavfile import write as write_wav
import pyperclip  # <-- Añadir este import


GROQ_API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
MODEL_NAME = "whisper-large-v3"
SAMPLE_RATE = 16000
RECORD_SECONDS = 5

listener_thread = None
stop_event = threading.Event()
recording = False
recording_bubble = None
audio_frames = []  # Renamed to avoid conflict

def create_recording_bubble():
    global recording_bubble
    try:
        x, y = pyautogui.position()
        y -= 100  
    except Exception as e:
        print(f"Error obteniendo posición: {e}")
        x, y = 100, 100  # Posición por defecto
    
    # Create bubble window
    recording_bubble = tk.Tk()
    recording_bubble.overrideredirect(True)
    recording_bubble.attributes("-topmost", True)
    recording_bubble.configure(bg='red')
    recording_bubble.geometry(f"120x40+{x}+{y}")
    
    # Add label
    label = tk.Label(recording_bubble, text="RECORDING...", bg='red', fg='white', 
                    font=("Arial", 10, "bold"))
    label.pack(fill=tk.BOTH, expand=True)
    
    # Bind click event to stop recording
    recording_bubble.bind("<Button-1>", lambda e: stop_recording())
    
    recording_bubble.update()

def stop_recording():
    global recording, recording_bubble
    recording = False
    if recording_bubble:
        recording_bubble.destroy()
        recording_bubble = None

def audio_callback(indata, frames_count, time, status):
    """Callback for the sounddevice InputStream"""
    global audio_frames  # Using the renamed global variable
    if recording:
        audio_frames.append(indata.copy())

def record_audio_continuous():
    global recording, audio_frames
    
    # Clear previous recordings
    audio_frames = []
    recording = True
    
    create_recording_bubble()
    
    print("Grabando audio continuamente... (haz clic en la burbuja o presiona ESC para detener)")
    
    try:
        # Start continuous recording
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback):
            while recording:
                if recording_bubble:
                    recording_bubble.update()  # Update the bubble GUI
                
                # Short sleep to prevent high CPU usage
                threading.Event().wait(0.1)
                
    except Exception as e:
        print(f"Error durante la grabación: {e}")
    finally:
        stop_recording()

    # Process all collected audio if recording was stopped properly
    if audio_frames:
        # Concatenate all audio frames
        audio_data = np.concatenate(audio_frames)
        return audio_data
    return None

def transcribe_with_groq(audio_data):
    if audio_data is None:
        return ""

    print("Convirtiendo audio a formato WAV...")
    wav_io = BytesIO()
    audio_int16 = np.int16(audio_data * 32767)
    write_wav(wav_io, SAMPLE_RATE, audio_int16)
    wav_io.seek(0)
    print("Audio convertido.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }

    files = {
        'file': ('audio.wav', wav_io, 'audio/wav')
    }
    data = {
        'model': MODEL_NAME,
    }

    print(f"Enviando audio a Groq API (modelo: {MODEL_NAME})...")
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
    if text:
        print("Escribiendo texto...")
        pyautogui.write(text, interval=0.01)
        print("Texto escrito.")
    else:
        print("No hay texto para escribir.")

def process_audio_and_transcribe():
    audio = record_audio_continuous()
    if audio is not None:
        text = transcribe_with_groq(audio)
        if text:
            write_text(text)
            print(f"Texto transcrito y escrito: {text}")
        else:
            print("No se pudo transcribir el audio.")
    else:
        print("No se grabó audio.")

def on_key_press(key):
    global listener_thread, recording
    try:
        if key == keyboard.Key.f8 and not recording:
            print("\nF8 presionado. Iniciando grabación continua...")
            processing_thread = threading.Thread(target=process_audio_and_transcribe, daemon=True)
            processing_thread.start()
        elif key == keyboard.Key.esc:
            if recording:
                print("\nEsc presionado. Deteniendo grabación...")
                stop_recording()
            else:
                print("\nEsc presionado. Deteniendo el listener...")
                stop_event.set()
                return False
    except AttributeError:
        pass
    except Exception as e:
        print(f"Error en on_key_press: {e}")

def main():
    global listener_thread
    print(f"Presiona F8 para iniciar la grabación continua (usando Groq API - {MODEL_NAME}).")
    print("Presiona Esc o haz clic en la burbuja de grabación para detener.")
    print("Presiona Esc cuando no estés grabando para salir del programa.")
    
    listener_thread = keyboard.Listener(on_press=on_key_press)
    listener_thread.start()
    stop_event.wait()
    print("Saliendo del programa...")
    
    # Ensure recording is stopped before exiting
    if recording:
        stop_recording()
    
    if listener_thread and listener_thread.is_alive():
        listener_thread.stop()

if __name__ == "__main__":
    try:
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = True
    except Exception as e:
         print(f"Error inicializando pyautogui: {e}")
    main()