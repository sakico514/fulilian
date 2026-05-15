from __future__ import annotations

from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget


class InteractionHandler(QObject):
    """Handles all mouse events on the pet window.

    Uses press_pos to distinguish drags from clicks. If the mouse moves
    less than 5 pixels (Manhattan distance) between press and release,
    it is treated as a click. Otherwise it is treated as a drag-to-move.
    """

    clicked = pyqtSignal()
    double_clicked = pyqtSignal()
    right_clicked = pyqtSignal(QPoint)

    def __init__(self, parent_window: QWidget) -> None:
        super().__init__(parent_window)
        self._window = parent_window
        self._drag_pos: QPoint | None = None
        self._press_pos: QPoint | None = None

    def handle_mouse_press(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.globalPosition().toPoint()
            self._press_pos = pos
            self._drag_pos = pos
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_clicked.emit(event.globalPosition().toPoint())

    def handle_mouse_move(self, event) -> None:
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._window.move(self._window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def handle_mouse_release(self, event) -> None:
        if self._press_pos is not None:
            total = event.globalPosition().toPoint() - self._press_pos
            if total.manhattanLength() < 5:
                self.clicked.emit()
        self._drag_pos = None
        self._press_pos = None

    def handle_mouse_double_click(self, event) -> None:
        self.double_clicked.emit()
