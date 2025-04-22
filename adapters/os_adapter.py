import os
import time
import platform
import subprocess
import pyautogui
import pyperclip
import json
from abc import ABC, abstractmethod

class OSAdapter(ABC):
    """Interfaz base para los adaptadores de sistema operativo"""
    
    @abstractmethod
    def save_active_window(self):
        """Guarda la ventana activa"""
        pass
    
    @abstractmethod
    def restore_active_window(self):
        """Restaura el foco a la ventana previamente guardada"""
        pass
    
    @abstractmethod
    def write_text(self, text):
        """Escribe texto en la ventana activa"""
        pass

class WindowsAdapter(OSAdapter):
    """Adaptador para Windows"""
    
    def __init__(self):
        self._saved_window = None
        
    def save_active_window(self):
        try:
            self._saved_window = pyautogui.getActiveWindow()
            print(f"Ventana activa guardada: {self._saved_window}")
        except Exception as e:
            print(f"Error al guardar la ventana activa: {e}")
            self._saved_window = None
            
    def restore_active_window(self):
        if not self._saved_window:
            print("No hay ventana guardada para restaurar.")
            return
            
        try:
            self._saved_window.activate()
            print("Ventana activada (Windows).")
            time.sleep(0.2)
        except Exception as e:
            print(f"Error al activar la ventana (Windows): {e}")
            
    def write_text(self, text):
        if not text:
            print("No hay texto para escribir.")
            return
            
        print("Escribiendo texto…")
        pyperclip.copy(text.strip())
        print("Texto copiado al portapapeles.")
        pyautogui.hotkey("ctrl", "v")
        print("Texto escrito.")

class MacOSAdapter(OSAdapter):
    """Adaptador para macOS"""
    
    def __init__(self):
        self._saved_window = None
        
    def save_active_window(self):
        try:
            self._saved_window = pyautogui.getActiveWindow()
            print(f"Ventana activa guardada: {self._saved_window}")
        except Exception as e:
            print(f"Error al guardar la ventana activa: {e}")
            self._saved_window = None
            
    def restore_active_window(self):
        if not self._saved_window:
            print("No hay ventana guardada para restaurar.")
            return
            
        try:
            self._saved_window.activate()
            print("Ventana activada (macOS).")
            time.sleep(0.2)
        except Exception as e:
            print(f"Error al activar la ventana (macOS): {e}")
            
    def write_text(self, text):
        if not text:
            print("No hay texto para escribir.")
            return
            
        print("Escribiendo texto…")
        pyperclip.copy(text.strip())
        print("Texto copiado al portapapeles.")
        # En macOS el atajo es command+v en lugar de ctrl+v
        pyautogui.hotkey("command", "v")
        print("Texto escrito.")

class LinuxX11Adapter(OSAdapter):
    """Adaptador para Linux con X11"""
    
    def __init__(self):
        self._saved_window = None
        
    def save_active_window(self):
        try:
            win_id = subprocess.check_output(
                ["xdotool", "getactivewindow"], stderr=subprocess.DEVNULL
            )
            self._saved_window = win_id.strip().decode()
            print(f"Ventana activa guardada (X11): {self._saved_window}")
        except Exception as e:
            print(f"Error al guardar la ventana activa (X11): {e}")
            self._saved_window = None
            
    def restore_active_window(self):
        if not self._saved_window:
            print("No hay ventana guardada para restaurar.")
            return
            
        try:
            subprocess.call(
                ["xdotool", "windowactivate", "--sync", self._saved_window],
                stderr=subprocess.DEVNULL,
            )
            print(f"Ventana activada (X11) con window id: {self._saved_window}")
            time.sleep(0.2)
        except Exception as e:
            print(f"Error al activar la ventana (X11): {e}")
            
    def write_text(self, text):
        if not text:
            print("No hay texto para escribir.")
            return
            
        print("Escribiendo texto…")
        pyperclip.copy(text.strip())
        print("Texto copiado al portapapeles.")
        pyautogui.hotkey("ctrl", "v")
        print("Texto escrito.")

class LinuxWaylandHyprlandAdapter(OSAdapter):
    """Adaptador para Linux con Wayland (Hyprland)"""
    
    def __init__(self):
        self._saved_window = None
        
    def save_active_window(self):
        try:
            out = subprocess.check_output(
                ["hyprctl", "clients", "-j"], stderr=subprocess.DEVNULL
            )
            clients = json.loads(out.decode())
            for c in clients:
                if c.get("focusHistoryID") == 0:
                    # guardamos la dirección única
                    self._saved_window = c.get("address")
                    print(f"Ventana activa guardada (Hyprland): {self._saved_window}")
                    return
        except Exception as e:
            print(f"Error al guardar la ventana activa (Hyprland): {e}")
            self._saved_window = None
            
    def restore_active_window(self):
        if not self._saved_window:
            print("No hay ventana guardada para restaurar.")
            return
            
        try:
            subprocess.call(
                ["hyprctl", "dispatch", "focuswindow", f"address:{self._saved_window}"],
                stderr=subprocess.DEVNULL,
            )
            print(f"Ventana activada (Hyprland) con address: {self._saved_window}")
            time.sleep(0.2)
        except Exception as e:
            print(f"Error al activar la ventana (Hyprland): {e}")
            
    def write_text(self, text):
        if not text:
            print("No hay texto para escribir.")
            return
            
        print("Escribiendo texto…")
        pyperclip.copy(text.strip())
        print("Texto copiado al portapapeles.")
        
        try:
            # Usar wtype para Hyprland
            subprocess.run(["wtype", "-M", "ctrl", "-P", "v", "-M", "ctrl", "-p", "v"], check=True)
            print("Texto escrito con wtype.")
        except Exception as e:
            print(f"Error al usar wtype: {e}, intentando con pyautogui...")
            pyautogui.hotkey("ctrl", "v")
            print("Texto escrito con pyautogui.")

    def get_cursor_position(self) -> tuple[int, int]:
        """Obtiene la posición actual del cursor en Hyprland
        
        Returns:
            tuple[int, int]: Coordenadas (x, y) de la posición del cursor
        """
        try:
            out = subprocess.check_output(["hyprctl", "cursorpos"], stderr=subprocess.DEVNULL)
            pos_str = out.decode().strip()
            # El formato esperado es: "X, Y"
            x, y = map(int, pos_str.split(','))
            print(f"Posición del cursor (Hyprland): ({x}, {y})")
            return (x, y)
        except Exception as e:
            print(f"Error al obtener la posición del cursor (Hyprland): {e}")
            return (0, 0)
        
class LinuxWaylandSwayAdapter(OSAdapter):
    """Adaptador para Linux con Wayland (Sway)"""
    
    def __init__(self):
        self._saved_window = None
        
    def save_active_window(self):
        try:
            out = subprocess.check_output(
                ["swaymsg", "-t", "get_tree"], stderr=subprocess.DEVNULL
            )
            tree = json.loads(out.decode())
            
            # función recursiva para buscar nodo con focus=true
            def find_focused(node):
                if node.get("focused"):
                    return node
                for ch in node.get("nodes", []) + node.get("floating_nodes", []):
                    res = find_focused(ch)
                    if res:
                        return res
                return None

            focused = find_focused(tree)
            if focused and "id" in focused:
                self._saved_window = focused["id"]
                print(f"Ventana activa guardada (Sway): {self._saved_window}")
        except Exception as e:
            print(f"Error al guardar la ventana activa (Sway): {e}")
            self._saved_window = None
            
    def restore_active_window(self):
        if not self._saved_window:
            print("No hay ventana guardada para restaurar.")
            return
            
        try:
            subprocess.call(
                ["swaymsg", f"[con_id={self._saved_window}]", "focus"],
                stderr=subprocess.DEVNULL,
            )
            print(f"Ventana activada (Sway) con con_id: {self._saved_window}")
            time.sleep(0.2)
        except Exception as e:
            print(f"Error al activar la ventana (Sway): {e}")
            
    def write_text(self, text):
        if not text:
            print("No hay texto para escribir.")
            return
            
        print("Escribiendo texto…")
        pyperclip.copy(text.strip())
        print("Texto copiado al portapapeles.")
        
        try:
            # Usar wtype para Sway
            subprocess.run(["wtype", "-M", "ctrl", "-P", "v", "-M", "ctrl", "-p", "v"], check=True)
            print("Texto escrito con wtype.")
        except Exception as e:
            print(f"Error al usar wtype: {e}, intentando con pyautogui...")
            pyautogui.hotkey("ctrl", "v")
            print("Texto escrito con pyautogui.")

class OSAdapterFactory:
    """Fábrica para crear el adaptador adecuado para el sistema operativo"""
    
    @staticmethod
    def create_adapter():
        system = platform.system()
        print(f"Sistema operativo detectado: {system}")
        
        # Windows
        if system == "Windows":
            print("Usando adaptador para Windows.")
            return WindowsAdapter()
            
        # macOS
        elif system == "Darwin":
            print("Usando adaptador para macOS.")
            return MacOSAdapter()
            
        # Linux
        elif system == "Linux":
            # Wayland
            if "WAYLAND_DISPLAY" in os.environ:
                # Hyprland
                if "HYPRLAND_INSTANCE_SIGNATURE" in os.environ:
                    print("Usando adaptador para Linux Wayland (Hyprland).")
                    return LinuxWaylandHyprlandAdapter()
                # Sway
                elif "SWAYSOCK" in os.environ:
                    print("Usando adaptador para Linux Wayland (Sway).")
                    return LinuxWaylandSwayAdapter()
                # Otros Wayland
                else:
                    print("Compositor Wayland no soportado específicamente, usando adaptador Wayland genérico.")
                    return LinuxWaylandHyprlandAdapter()  # Usamos Hyprland como fallback
            # X11
            else:
                print("Usando adaptador para Linux X11.")
                return LinuxX11Adapter()
                
        # Sistema no soportado
        else:
            raise NotImplementedError(f"Sistema operativo no soportado: {system}")