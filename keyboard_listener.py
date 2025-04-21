"""
Módulo para gestionar los eventos del teclado
"""
import threading
from pynput import keyboard
from audio_recorder import record_audio_continuous, is_recording, stop_recording
from transcription import write_text, get_transcriber

# Variables de estado del teclado
listener_thread = None
stop_event = threading.Event()
command_key = "f8"  # Por defecto

def process_audio_and_transcribe(sample_rate):
    """Procesa el audio grabado, lo transcribe y escribe el resultado"""
    audio = record_audio_continuous()
    if audio is not None:
        text = get_transcriber().transcribe(audio, sample_rate)
        if text:
            write_text(text)
            print(f"Texto transcrito y escrito: {text}")
        else:
            print("No se pudo transcribir el audio.")
    else:
        print("No se grabó audio.")


def trigger_transcription(config):
    """Función para activar la transcripción desde otra instancia"""
    if not is_recording():
        print("\nActivando transcripción por solicitud remota...")
        processing_thread = threading.Thread(
            target=lambda: process_audio_and_transcribe(16000), 
            daemon=True
        )
        processing_thread.start()
        return True
    else:
        print("\nYa hay una transcripción en curso, ignorando solicitud remota.")
        return False


def on_key_press(key):
    """Manejador de eventos de teclado"""
    global command_key
    
    try:
        if hasattr(key, "name") and key.name == command_key and not is_recording():
            print(f"\n{command_key.upper()} presionado. Iniciando grabación continua...")
            processing_thread = threading.Thread(
                target=lambda: process_audio_and_transcribe(16000), 
                daemon=True
            )
            processing_thread.start()
        elif key == keyboard.Key.esc:
            if is_recording():
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

def start_keyboard_listener(config):
    """Inicia el listener del teclado"""
    global listener_thread, command_key
    
    # Actualizar la tecla de comando desde la configuración
    command_key = config["command_key"]
    
    # Iniciar el listener del teclado
    listener_thread = keyboard.Listener(on_press=on_key_press)
    listener_thread.start()
    
    # Esperar a que se active el evento de parada
    stop_event.wait()
    
    # Limpiar al salir
    if listener_thread and listener_thread.is_alive():
        listener_thread.stop()