"""
Módulo para grabación de audio
"""
import threading
import tkinter as tk
import pyautogui
import sounddevice as sd
import numpy as np

# Variables globales del módulo
recording = False
recording_bubble = None
audio_frames = []
sample_rate = 16000  # valor por defecto

def setup_recorder(config):
    """Configura el grabador de audio con los parámetros dados"""
    global sample_rate
    sample_rate = config["sample_rate"]

def create_recording_bubble():
    """Crea una burbuja visual que indica que se está grabando"""
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
    """Detiene la grabación y elimina la burbuja visual"""
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
    """Graba audio continuamente hasta que se detiene manualmente"""
    global recording, audio_frames
    
    # Limpiar grabaciones previas
    audio_frames = []
    recording = True
    
    create_recording_bubble()
    
    print("Grabando audio continuamente... (haz clic en la burbuja o presiona ESC para detener)")
    
    try:
        # Iniciar grabación continua
        with sd.InputStream(samplerate=sample_rate, channels=1, callback=audio_callback):
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

def is_recording():
    """Devuelve si actualmente se está grabando"""
    return recording