"""
Gestión de la configuración de la aplicación usando .env
"""
import os
import tkinter as tk
from tkinter import ttk
from dotenv import load_dotenv, set_key

ENV_FILE = ".env"

def load_config():
    """Carga la configuración desde .env o usa valores predeterminados"""
    # Carga variables de entorno desde el archivo .env (si existe)
    load_dotenv(dotenv_path=ENV_FILE)

    return {
        "groq_api_key": os.getenv("GROQ_API_KEY", ""),
        "command_key": os.getenv("COMMAND_KEY", "f8").lower()
    }

def save_config(config):
    """Guarda la configuración en el archivo .env"""
    # Asegura que exista el archivo .env
    if not os.path.exists(ENV_FILE):
        open(ENV_FILE, 'a').close()

    # Mapeo de claves internas a variables de entorno
    mapping = {
        "groq_api_key": "GROQ_API_KEY",
        "command_key": "COMMAND_KEY"
    }

    for key, env_key in mapping.items():
        value = config.get(key, "")
        set_key(ENV_FILE, env_key, value)

def show_configuration(config):
    """Muestra una ventana de configuración y devuelve la configuración actualizada"""
    result_config = config.copy()

    def guardar_config():
        result_config["groq_api_key"] = api_entry.get().strip()
        result_config["command_key"] = command_entry.get().strip().lower()
        save_config(result_config)
        config_window.destroy()

    config_window = tk.Tk()
    config_window.title("Configuración")
    config_window.resizable(False, False)

    frame = ttk.Frame(config_window, padding="10")
    frame.grid(row=0, column=0)

    # Campo para Groq API Key
    ttk.Label(frame, text="API Key Groq:").grid(row=0, column=0, sticky="w")
    api_entry = ttk.Entry(frame, width=50)
    api_entry.insert(0, config.get("groq_api_key", ""))
    api_entry.grid(row=0, column=1, pady=5)

    # Campo para Tecla de grabación
    ttk.Label(frame, text="Tecla de grabación (ej: f8):").grid(row=1, column=0, sticky="w")
    command_entry = ttk.Entry(frame, width=10)
    command_entry.insert(0, config.get("command_key", "f8"))
    command_entry.grid(row=1, column=1, pady=5, sticky="w")

    # Botón para guardar
    guardar_btn = ttk.Button(frame, text="Guardar", command=guardar_config)
    guardar_btn.grid(row=2, column=0, columnspan=2, pady=10)

    config_window.mainloop()
    return result_config