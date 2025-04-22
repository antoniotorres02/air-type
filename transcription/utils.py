import os
import time
import platform
import subprocess
import pyautogui
import pyperclip
import json

# Variable global para guardar la referencia/ID de la ventana
_saved_window = None

def save_active_window() -> None:
    """
    Guarda la ventana activa en la variable global _saved_window.
      - En Windows/macOS usa pyautogui.getActiveWindow()
      - En Linux/X11 usa xdotool getactivewindow
      - En Linux/Wayland usa swaymsg o hyprctl
    """
    global _saved_window
    system = platform.system()

    print(f"Sistema operativo detectado: {system}")

    # --- Windows / macOS ---------------------------------------------------
    if system in ("Windows", "Darwin"):
        print("Sistema Windows o macOS detectado.")
        try:
            _saved_window = pyautogui.getActiveWindow()
            print(f"Ventana activa guardada: {_saved_window}")
            return
        except Exception as e:
            print(f"Error al guardar la ventana activa: {e}")
            _saved_window = None
            print("Ventana activa establecida a None.")

    # --- Linux + Wayland ---------------------------------------------------
    if system == "Linux" and "WAYLAND_DISPLAY" in os.environ:
        print("Sistema Linux con Wayland detectado.")
        # Hyprland
        if "HYPRLAND_INSTANCE_SIGNATURE" in os.environ:
            print("Hyprland detectado.")
            try:
                out = subprocess.check_output(
                    ["hyprctl", "clients", "-j"], stderr=subprocess.DEVNULL
                )
                clients = json.loads(out.decode())
                for c in clients:
                    if c.get("focusHistoryID") == 0 :
                        # guardamos la dirección única
                        _saved_window = {
                            "compositor": "hyprland",
                            "address": c.get("address"),
                        }
                        print(f"Ventana activa guardada (Hyprland): {_saved_window}")
                        return
            except Exception as e:
                print(f"Error al guardar la ventana activa (Hyprland): {e}")
                _saved_window = None
                print("Ventana activa establecida a None.")
                return
        # Sway (y wlroots compatibles)
        elif "SWAYSOCK" in os.environ:
            print("Sway detectado.")
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
                    _saved_window = {
                        "compositor": "sway",
                        "id": focused["id"],
                    }
                    print(f"Ventana activa guardada (Sway): {_saved_window}")
                    return
            except Exception as e:
                print(f"Error al guardar la ventana activa (Sway): {e}")
                _saved_window = None
                print("Ventana activa establecida a None.")
                return

        # otros Wayland no soportados
        print("Compositor Wayland no soportado.")
        _saved_window = None
        print("Ventana activa establecida a None.")
        return

    # --- Linux + X11 --------------------------------------------------------
    if system == "Linux" and "WAYLAND_DISPLAY" not in os.environ:
        print("Sistema Linux con X11 detectado.")
        try:
            win_id = subprocess.check_output(
                ["xdotool", "getactivewindow"], stderr=subprocess.DEVNULL
            )
            _saved_window = win_id.strip().decode()
            print(f"Ventana activa guardada (X11): {_saved_window}")
        except Exception as e:
            print(f"Error al guardar la ventana activa (X11): {e}")
            _saved_window = None
            print("Ventana activa establecida a None.")
        return

    # por defecto
    print("Sistema no detectado o no soportado.")
    _saved_window = None
    print("Ventana activa establecida a None (por defecto).")

def restore_active_window() -> None:
    """
    Restaura el foco a la ventana previamente guardada.
      - En Windows/macOS usa el método .activate() de pyautogui
      - En Linux/X11 usa xdotool windowactivate
      - En Linux/Wayland usa swaymsg o hyprctl
    """
    system = platform.system()
    if not _saved_window:
        print("No hay ventana guardada para restaurar.")
        return

    print("Restaurando ventana activa...")

    # --- Windows / macOS ---
    if system in ("Windows", "Darwin") and hasattr(_saved_window, "activate"):
        print("Sistema Windows o macOS detectado.")
        try:
            _saved_window.activate()
            print("Ventana activada (Windows/macOS).")
            time.sleep(0.2)
            return
        except Exception as e:
            print(f"Error al activar la ventana (Windows/macOS): {e}")
            pass  # caerá al siguiente bloque

    # --- Linux + Wayland ---
    if system == "Linux" and isinstance(_saved_window, dict):
        print("Sistema Linux con Wayland detectado.")
        comp = _saved_window.get("compositor")
        if comp == "hyprland":
            print("Hyprland detectado.")
            addr = _saved_window.get("address")
            if addr:
                subprocess.call(
                    ["hyprctl", "dispatch", "focuswindow", f"address:{addr}"],
                    stderr=subprocess.DEVNULL,
                )
                print(f"Ventana activada (Hyprland) con address: {addr}")
                time.sleep(0.2)
                return
        elif comp == "sway":
            print("Sway detectado.")
            con_id = _saved_window.get("id")
            if con_id:
                subprocess.call(
                    ["swaymsg", f"[con_id={con_id}]", "focus"],
                    stderr=subprocess.DEVNULL,
                )
                print(f"Ventana activada (Sway) con con_id: {con_id}")
                time.sleep(0.2)
                return

    # --- Linux + X11 ---
    if system == "Linux" and isinstance(_saved_window, str):
        print("Sistema Linux con X11 detectado.")
        subprocess.call(
            ["xdotool", "windowactivate", "--sync", _saved_window],
            stderr=subprocess.DEVNULL,
        )
        print(f"Ventana activada (X11) con window id: {_saved_window}")
        time.sleep(0.2)

def write_text(text: str) -> None:
    """
    Escribe el texto en el portapapeles y pega con Ctrl+V
    en la ventana que estaba activa cuando se llamó a save_active_window().
    """
    if not text:
        print("No hay texto para escribir.")
        return

    print("Escribiendo texto…")
    pyperclip.copy(text.strip())

    print("Texto copiado al portapapeles.")

    # Restaurar foco antes de pegar
    # restore_active_window()

    # Pegar (CTRL-V)
    
    system = platform.system()
    if system == "Linux" and "WAYLAND_DISPLAY" in os.environ:
        print("Sistema Linux con Wayland detectado.")
        # Hyprland
        if "HYPRLAND_INSTANCE_SIGNATURE" in os.environ:
            try:
                subprocess.run(["wtype", "-M", "ctrl", "-P", "v", "-M", "ctrl", "-p", "v"], check=True)                
            except Exception as e:
                print(f"Error al pegar (Hyprland): {e}")
                return


    pyautogui.hotkey("ctrl", "v")
    print("Texto escrito.")
