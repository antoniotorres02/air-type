"""
Módulo para grabación de audio
"""
import threading
import tkinter as tk
import pyautogui
import sounddevice as sd
import numpy as np
from transcription import BubbleManager, bubble_manager

from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtCore import QTimer
import os



# Variables globales del módulo
recording = False
recording_bubble = None
audio_frames = []
sample_rate = 16000  # valor por defecto

def setup_recorder(config):
    """Configura el grabador de audio con los parámetros dados"""
    global sample_rate
    sample_rate = int(os.getenv("SAMPLE_RATE", "16000"))

def audio_callback(indata, frames_count, time, status):
    """Callback para el InputStream de sounddevice"""
    global audio_frames
    if recording:
        audio_frames.append(indata.copy())

def record_audio_continuous():
    """Graba audio continuamente hasta que se detiene manualmente.
    
    Args:
        bubble_manager: Instancia de BubbleManager para mostrar/ocultar la burbuja.
    """
    global audio_frames
    global recording
    recording = True
    audio_frames = [] 
    # Conectar la señal de cierre de la burbuja para detener la grabación


    bubble_manager.bubble_closed.connect(stop_recording)
    bubble_manager.show_bubble.emit()  # Mostrar la burbuja
    
    print("Grabando audio continuamente... (haz clic en la burbuja o presiona ESC para detener)")

    try:
        with sd.InputStream(samplerate=sample_rate, channels=1, callback=audio_callback):
            while recording:
                # Pequeña pausa para evitar alto uso de CPU
                if bubble_manager.recording_bubble == None:
                    stop_recording()
                threading.Event().wait(0.5)

    except Exception as e:
        print(f"Error durante la grabación: {e}")
    finally:
        if recording:
            recording = False
            bubble_manager._hide_bubble()  # Asegurarse de cerrar la burbuja

    # Procesar todo el audio recogido si la grabación se detuvo correctamente
    if audio_frames:
        audio_data = np.concatenate(audio_frames)
        return audio_data
    return None

def is_recording():
    """Devuelve si actualmente se está grabando"""
    return recording

def stop_recording():
    global recording
    recording = False