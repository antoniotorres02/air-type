"""
Aplicación principal de transcripción de voz
Punto de entrada que coordina los diferentes módulos
"""
import pyautogui
from config import load_config, show_configuration
from audio_recorder import setup_recorder, stop_recording
from transcription import setup_transcription
from keyboard_listener import start_keyboard_listener, trigger_transcription
from socket_server import is_server_running, start_server, stop_server, send_trigger_command
import sys

def main():
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1 and sys.argv[1] == "--transcript":
        # Modo cliente: intentar comunicarse con la instancia principal
        if is_server_running():
            print("Instancia principal detectada, enviando solicitud de transcripción...")
            if send_trigger_command():
                print("Solicitud de transcripción enviada correctamente.")
                sys.exit(0)
            else:
                print("Error al enviar la solicitud. Iniciando como instancia principal...")
        else:
            print("No se detectó ninguna instancia principal. Iniciando como instancia principal...")
    
    config = load_config()
    config = show_configuration(config)
    
    setup_recorder(config)
    setup_transcription(config)
    
    print(f"Presiona {config['command_key'].upper()} para iniciar la grabación continua")
    print(f"(usando Groq API - {config['model_name']}).")
    print("Presiona Esc o haz clic en la burbuja de grabación para detener.")
    print("Presiona Esc cuando no estés grabando para salir del programa.")
    
    
    # Iniciar el servidor socket
    start_server(lambda: trigger_transcription(config))
    
    # Iniciar el listener del teclado
    try:
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = True
    except Exception as e:
        print(f"Error inicializando pyautogui: {e}")
        
    start_keyboard_listener(config)
    
    stop_recording()

if __name__ == "__main__":
    main()