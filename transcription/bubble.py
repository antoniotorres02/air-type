from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QMouseEvent, QCursor
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QObject, pyqtSignal
from .utils import get_cursor_position

class BubbleManager(QObject):
    show_bubble = pyqtSignal()
    bubble_closed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.show_bubble.connect(self._show_bubble_impl)
        self.recording_bubble = None

    def _show_bubble_impl(self):
        """Crea una burbuja de transcripción con PyQt5"""
        self.is_closed = False
        self.recording_bubble = QWidget()
        self.recording_bubble.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.recording_bubble.setAttribute(Qt.WA_TranslucentBackground)
        
        # Contenedor principal que tendrá el fondo blanco
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 1px solid #d3d3d3;
                border-radius: 10px;
            }
            QLabel {
                border: none;
            }
        """)
        
        # Labels sin fondo
        label_main = QLabel("TRANSCRIPTING...")
        label_main.setStyleSheet("""
            font: bold 12px Arial;
            color: black;
        """)
        label_main.setAlignment(Qt.AlignCenter)

        label_sub = QLabel("Press ESC or click to stop...")
        label_sub.setStyleSheet("""
            font: 8px Arial;
            color: #555555;
        """)
        label_sub.setAlignment(Qt.AlignCenter)

        # Layout para el contenedor
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 5, 10, 5)
        container_layout.setSpacing(2)
        container_layout.addWidget(label_main)
        container_layout.addWidget(label_sub)

        # Layout principal
        main_layout = QVBoxLayout(self.recording_bubble)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        self.recording_bubble.setFixedSize(200, 60)

        # Posicionamiento
        cursor_pos = get_cursor_position()
        
        x, y = cursor_pos

        self.recording_bubble.move(x, y - 100)
        print(f"Moving recording bubble to x={x}, y={y - 100}")

        # Eventos
        def mousePressEvent(event: QMouseEvent):
            if event.button() == Qt.LeftButton:
                self._hide_bubble()

        self.recording_bubble.mousePressEvent = mousePressEvent
        self.recording_bubble.keyPressEvent = lambda e: self._hide_bubble() if e.key() == Qt.Key_Escape else None
        self.recording_bubble.show()

    def _hide_bubble(self):
        """Cierra la burbuja y emite la señal de cierre."""
        if self.recording_bubble:
            self.recording_bubble.close()
            self.recording_bubble = None
            self.bubble_closed.emit()


bubble_manager = BubbleManager()