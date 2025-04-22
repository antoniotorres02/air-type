from adapters import OSAdapterFactory

# Inicializar el adaptador adecuado al importar el módulo
_os_adapter = OSAdapterFactory.create_adapter()

def save_active_window() -> None:
    """Guarda la ventana activa en el adaptador del SO"""
    _os_adapter.save_active_window()

def restore_active_window() -> None:
    """Restaura el foco a la ventana previamente guardada"""
    _os_adapter.restore_active_window()

def write_text(text: str) -> None:
    """Escribe el texto en la ventana activa"""
    _os_adapter.write_text(text)


def get_cursor_position() -> tuple[int, int]:
    """Obtiene la posición actual del cursor en la pantalla
    
    Returns:
        tuple[int, int]: Coordenadas (x, y) de la posición del cursor
    """
    return _os_adapter.get_cursor_position()