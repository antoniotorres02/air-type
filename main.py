import sounddevice as sd
import numpy as np
import requests
import pyautogui
import threading
import json
import tkinter as tk
from tkinter import ttk
from pynput import keyboard
from io import BytesIO
from scipy.io.wavfile import write as write_wav
import pyperclip  # <-- Añadido este import

# Variables de configuración globales (se pueden modificar desde la interfaz)
GROQ_API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
MODEL_NAME = "whisper-large-v3"
SAMPLE_RATE = 16000
RECORD_SECONDS = 5
command_key = "f8"  # Por defecto, la tecla para activar la grabación

listener_thread = None
stop_event = threading.Event()
recording = False
recording_bubble = None
audio_frames = []  # Renombrado para evitar conflicto

def create_recording_bubble():
    global recording_bubble
    try:
        x, y = pyautogui.position()
        y -= 100  
    except Exception as e:
        print(f"Error obteniendo posición: {e}")
        x, y = 100, 100  # Posición por defecto
    
    # Crear la ventana burbuja
    recording_bubble = tk.Tk()
    recording_bubble.overrideredirect(True)
    recording_bubble.attributes("-topmost", True)
    recording_bubble.configure(bg='red')
    recording_bubble.geometry(f"120x40+{x}+{y}")
    
    # Agregar etiqueta
    label = tk.Label(recording_bubble, text="RECORDING...", bg='red', fg='white', 
                    font=("Arial", 10, "bold"))
    label.pack(fill=tk.BOTH, expand=True)
    
    # Vincular el click para detener la grabación
    recording_bubble.bind("<Button-1>", lambda e: stop_recording())
    
    recording_bubble.update()

def stop_recording():
    global recording, recording_bubble
    recording = False
    if recording_bubble:
        recording_bubble.destroy()
        recording_bubble = None

def audio_callback(indata, frames_count, time, status):
    """Callback para el InputStream de sounddevice"""
    global audio_frames
    if recording:
        audio_frames.append(indata.copy())

def record_audio_continuous():
    global recording, audio_frames
    
    # Limpiar grabaciones previas
    audio_frames = []
    recording = True
    
    create_recording_bubble()
    
    print("Grabando audio continuamente... (haz clic en la burbuja o presiona ESC para detener)")
    
    try:
        # Iniciar grabación continua
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback):
            while recording:
                if recording_bubble:
                    recording_bubble.update()  # Actualizar GUI de la burbuja
                
                # Pequeña pausa para evitar alto uso de CPU
                threading.Event().wait(0.1)
                
    except Exception as e:
        print(f"Error durante la grabación: {e}")
    finally:
        stop_recording()

    # Procesar todo el audio recogido si la grabación se detuvo correctamente
    if audio_frames:
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
    global listener_thread, recording, command_key
    try:
        if hasattr(key, "name") and key.name == command_key and not recording:
            print(f"\n{command_key.upper()} presionado. Iniciando grabación continua...")
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

def show_configuration():
    """Muestra una ventana de configuración para cambiar la API key de Groq y el comando de grabación"""
    def guardar_config():
        global GROQ_API_KEY, command_key
        # Actualizar variables globales
        GROQ_API_KEY = api_entry.get().strip()
        # Convertir el comando a minúsculas para su comparación en on_key_press
        command_key = command_entry.get().strip().lower()
        config_window.destroy()
    
    config_window = tk.Tk()
    config_window.title("Configuración")
    config_window.resizable(False, False)
    
    frame = ttk.Frame(config_window, padding="10")
    frame.grid(row=0, column=0)
    
    # Campo para Groq API Key
    ttk.Label(frame, text="API Key Groq:").grid(row=0, column=0, sticky="w")
    api_entry = ttk.Entry(frame, width=50)
    api_entry.insert(0, GROQ_API_KEY)
    api_entry.grid(row=0, column=1, pady=5)
    
    # Campo para comando
    ttk.Label(frame, text="Tecla de grabación (ej: f8):").grid(row=1, column=0, sticky="w")
    command_entry = ttk.Entry(frame, width=10)
    command_entry.insert(0, command_key)
    command_entry.grid(row=1, column=1, pady=5, sticky="w")
    
    # Botón para guardar
    guardar_btn = ttk.Button(frame, text="Guardar", command=guardar_config)
    guardar_btn.grid(row=2, column=0, columnspan=2, pady=10)
    
    # Ejecutar la ventana de configuración de forma bloqueante
    config_window.mainloop()

def main():
    global listener_thread
    # Mostrar la interfaz de configuración antes de iniciar el listener
    show_configuration()
    
    print(f"Presiona {command_key.upper()} para iniciar la grabación continua (usando Groq API - {MODEL_NAME}).")
    print("Presiona Esc o haz clic en la burbuja de grabación para detener.")
    print("Presiona Esc cuando no estés grabando para salir del programa.")
    
    listener_thread = keyboard.Listener(on_press=on_key_press)
    listener_thread.start()
    stop_event.wait()
    print("Saliendo del programa...")
    
    # Asegurarse de que la grabación se detenga antes de salir
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