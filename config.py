"""
Gestión de la configuración de la aplicación
"""
import os
import json
import tkinter as tk
from tkinter import ttk

# Valores por defecto
DEFAULT_CONFIG = {
    "groq_api_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "model_name": "whisper-large-v3",
    "sample_rate": 16000,
    "command_key": "f8"
}

CONFIG_FILE = "app_config.json"

def load_config():
    """Carga la configuración desde un archivo JSON o usa valores predeterminados"""
    config = DEFAULT_CONFIG.copy()
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                stored_config = json.load(f)
                config.update(stored_config)
    except Exception as e:
        print(f"Error cargando configuración: {e}")
    
    return config

def save_config(config):
    """Guarda la configuración en un archivo JSON"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error guardando configuración: {e}")

def show_configuration(config):
    """Muestra una ventana de configuración y devuelve la configuración actualizada"""
    result_config = config.copy()
    
    def guardar_config():
        # Actualizar la configuración con los valores de la interfaz
        result_config["groq_api_key"] = api_entry.get().strip()
        result_config["command_key"] = command_entry.get().strip().lower()
        
        # Guardar la configuración actualizada
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
    api_entry.insert(0, config["groq_api_key"])
    api_entry.grid(row=0, column=1, pady=5)
    
    # Campo para comando
    ttk.Label(frame, text="Tecla de grabación (ej: f8):").grid(row=1, column=0, sticky="w")
    command_entry = ttk.Entry(frame, width=10)
    command_entry.insert(0, config["command_key"])
    command_entry.grid(row=1, column=1, pady=5, sticky="w")
    
    # Botón para guardar
    guardar_btn = ttk.Button(frame, text="Guardar", command=guardar_config)
    guardar_btn.grid(row=2, column=0, columnspan=2, pady=10)
    
    # Ejecutar la ventana de configuración de forma bloqueante
    config_window.mainloop()
    
    return result_config