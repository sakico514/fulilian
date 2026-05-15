from __future__ import annotations

from PyQt6.QtCore import Qt, QPoint, QSize, pyqtSignal
from PyQt6.QtGui import QFont, QPainter, QColor, QBrush, QPen
from PyQt6.QtWidgets import QLineEdit, QWidget


class ChatInput(QWidget):
    submitted = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText("和芙莉莲说点什么...")
        self.input.setMinimumWidth(280)
        self.input.setFixedHeight(44)
        font = QFont("Microsoft YaHei", 12)
        self.input.setFont(font)
        self.input.setStyleSheet("""
            QLineEdit {
                color: #1a1a2e;
                background-color: rgba(255, 255, 255, 245);
                border: 1px solid rgba(0, 0, 0, 10);
                border-radius: 22px;
                padding: 0px 20px;
                selection-background-color: #a0c4ff;
            }
            QLineEdit:focus {
                border: 1px solid #6c9ce0;
            }
        """)
        self.input.returnPressed.connect(self._on_submit)

        self.setFixedSize(self.input.sizeHint().width() + 16, 52)
        self.input.setGeometry(8, 4, self.input.sizeHint().width(), 44)

    def _on_submit(self) -> None:
        text = self.input.text().strip()
        if text:
            self.submitted.emit(text)
            self.input.clear()

    def show_at(self, pos: QPoint, owner_size: QSize) -> None:
        self.adjustSize()
        x = pos.x() + owner_size.width() // 2 - self.width() // 2
        y = pos.y() + owner_size.height() + 6
        self.move(max(0, x), max(0, y))
        self.show()
        self.input.setFocus()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(255, 255, 255, 238)))
        painter.setPen(QPen(QColor(0, 0, 0, 12), 1))
        painter.drawRoundedRect(4, 4, self.width() - 8, 44, 22, 22)
        painter.end()
