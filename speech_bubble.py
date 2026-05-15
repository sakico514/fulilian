from __future__ import annotations

from PyQt6.QtCore import Qt, QPoint, QSize, QTimer, QRect
from PyQt6.QtGui import QFont, QFontMetrics, QPainter, QPolygon, QColor, QBrush, QPen
from PyQt6.QtWidgets import QLabel, QWidget

MIN_WIDTH = 160
MAX_WIDTH = 360


class SpeechBubble(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setFont(QFont("Microsoft YaHei", 12))
        self.label.setStyleSheet("""
            QLabel {
                color: #1a1a2e;
                padding: 14px 18px;
                background: transparent;
            }
        """)

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.fade_out)

        self._tail_h = 8

    def show_text(
        self,
        text: str,
        owner_pos: QPoint,
        owner_size: QSize,
        duration_ms: int = 5000,
    ) -> None:
        self.label.setText(text)

        fm = QFontMetrics(self.label.font())
        pad = 36  # 18px padding on each side

        # Calculate required width
        single_line_w = fm.horizontalAdvance(text) + pad
        if single_line_w <= MAX_WIDTH:
            label_w = max(single_line_w, MIN_WIDTH)
        else:
            label_w = MAX_WIDTH

        # Calculate height at this width with word wrap
        text_rect = fm.boundingRect(
            QRect(0, 0, label_w - pad, 0),
            Qt.TextFlag.TextWordWrap | Qt.TextFlag.TextExpandTabs,
            text,
        )
        label_h = text_rect.height() + 32  # 14px padding top+bottom + some slack

        self.label.setFixedSize(label_w, label_h)
        self.label.setMaximumWidth(label_w)

        total_w = label_w
        total_h = label_h + self._tail_h
        self.setFixedSize(total_w, total_h)

        x = owner_pos.x() + owner_size.width() // 2 - total_w // 2
        y = owner_pos.y() - total_h - 6
        self.move(max(0, x), max(0, y))
        self.show()
        if duration_ms > 0:
            self._hide_timer.start(duration_ms)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.label.height()
        r = 16
        th = self._tail_h

        # Bubble body
        painter.setBrush(QBrush(QColor(255, 255, 255, 248)))
        painter.setPen(QPen(QColor(0, 0, 0, 15), 1))
        painter.drawRoundedRect(0, 0, w, h, r, r)

        # Tail triangle
        cx = w // 2
        tail = QPolygon()
        tail.append(QPoint(cx - 6, h))
        tail.append(QPoint(cx + 6, h))
        tail.append(QPoint(cx, h + th))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 248)))
        painter.drawPolygon(tail)

        painter.end()

    def fade_out(self) -> None:
        self._hide_timer.stop()
        self.hide()
