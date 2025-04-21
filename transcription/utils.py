"""
Funciones utilitarias para transcripción.
"""
import pyautogui
import pyperclip

def write_text(text: str) -> None:
    """Escribe el texto usando el portapapeles y autogui."""
    if text:
        print("Escribiendo texto...")
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        print("Texto escrito.")
    else:
        print("No hay texto para escribir.")