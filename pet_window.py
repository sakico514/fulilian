from __future__ import annotations

import os
import random

from PyQt6.QtWidgets import QWidget, QLabel, QMenu, QHBoxLayout
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QAction, QCursor

from animation_manager import AnimationManager
from behavior_engine import BehaviorEngine
from interaction_handler import InteractionHandler
from speech_bubble import SpeechBubble
from chat_input import ChatInput
from ai_engine import AIEngine
from ai_config import get_api_key, AI_SETTINGS
from desktop_context import get_desktop_context
import app_actions

import re


class PetWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setMouseTracking(True)

        # Label for GIF display
        self.label = QLabel(self)
        self.label.setStyleSheet("background: transparent;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setScaledContents(True)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)

        # Animation manager — default to 50% scale
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self.anim_manager = AnimationManager(assets_dir, scale=0.5, parent=self)
        self.anim_manager.load_all()

        size = self.anim_manager.target_size
        if size:
            self.label.setFixedSize(size)
            self.setFixedSize(size)
        else:
            self.setFixedSize(200, 200)
            self.label.setFixedSize(200, 200)

        self.anim_manager.set_label(self.label)
        self.anim_manager.switch_state("idle")

        # Behavior engine
        self.behavior = BehaviorEngine(self.anim_manager, self)
        self.behavior.move_by.connect(self._on_move_by)
        self.behavior.start_auto_behavior(5000, 15000)

        # Interaction handler
        self.interaction = InteractionHandler(self)
        self.interaction.clicked.connect(self._on_click)
        self.interaction.double_clicked.connect(self._on_double_click)
        self.interaction.right_clicked.connect(self._on_right_click)

        # AI engine
        api_key = get_api_key()
        self.ai_engine = AIEngine(api_key) if api_key else None
        self._waiting_for_reply = False

        # Speech bubble and chat input
        self.speech_bubble = SpeechBubble()
        self.chat_input = ChatInput()
        self.chat_input.submitted.connect(self._on_chat_submit)

        # Auto-speak timer
        self._auto_speak_timer = QTimer(self)
        self._auto_speak_timer.timeout.connect(self._auto_speak)
        self._schedule_auto_speak()

    def paintEvent(self, event) -> None:
        pass

    def set_scale(self, scale: float) -> None:
        new_size = self.anim_manager.set_scale(scale)
        if new_size:
            self.label.setFixedSize(new_size)
            self.setFixedSize(new_size)

    def _on_move_by(self, dx: int, dy: int) -> None:
        screen = self.screen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        new_x = self.x() + dx
        new_y = self.y() + dy

        # Bounce at screen edges — flip running direction
        if new_x < geo.left():
            new_x = geo.left()
            self.behavior.flip_direction()
        elif new_x + self.width() > geo.right():
            new_x = geo.right() - self.width()
            self.behavior.flip_direction()

        # Clamp vertically (jump won't go off screen)
        if new_y < geo.top():
            new_y = geo.top()
        elif new_y + self.height() > geo.bottom():
            new_y = geo.bottom() - self.height()

        self.move(new_x, new_y)

    def _schedule_auto_speak(self) -> None:
        sec = random.randint(
            AI_SETTINGS["auto_speak_min_sec"],
            AI_SETTINGS["auto_speak_max_sec"],
        )
        self._auto_speak_timer.start(sec * 1000)

    def _get_context(self) -> str:
        pos = self.pos()
        sz = self.size()
        return get_desktop_context(pos.x(), pos.y(), sz.width(), sz.height())

    def _auto_speak(self) -> None:
        self._auto_speak_timer.stop()
        if self.ai_engine and self.ai_engine.is_available() and not self._waiting_for_reply:
            ctx = self._get_context()
            prompt = (
                f"（自言自语，作为桌宠，1-2句，语气慵懒。"
                f"桌面状态：{ctx}）"
            )
            self._waiting_for_reply = True
            self.speech_bubble.show_text("...", self.pos(), self.size(), duration_ms=0)
            self.ai_engine.send_message_async(prompt, self._on_ai_reply)
        self._schedule_auto_speak()

    def mousePressEvent(self, event) -> None:
        self.interaction.handle_mouse_press(event)

    def mouseMoveEvent(self, event) -> None:
        self.interaction.handle_mouse_move(event)

    def mouseReleaseEvent(self, event) -> None:
        self.interaction.handle_mouse_release(event)

    def mouseDoubleClickEvent(self, event) -> None:
        self.interaction.handle_mouse_double_click(event)

    def _on_click(self) -> None:
        self.behavior.react_to_click()
        self.chat_input.show_at(self.pos(), self.size())

    def _on_double_click(self) -> None:
        self.behavior.react_to_double_click()
        self.chat_input.show_at(self.pos(), self.size())

    def _on_right_click(self, _pos: QPoint) -> None:
        menu = QMenu(self)

        act = QAction("待机", self)
        act.triggered.connect(lambda: self.behavior.set_state("idle"))
        menu.addAction(act)

        act = QAction("挥手", self)
        act.triggered.connect(lambda: self.behavior.set_state("waving"))
        menu.addAction(act)

        act = QAction("跳跃", self)
        act.triggered.connect(lambda: self.behavior.set_state("jumping"))
        menu.addAction(act)

        act = QAction("走动", self)
        act.triggered.connect(lambda: self.behavior.set_state("running"))
        menu.addAction(act)

        act = QAction("审视", self)
        act.triggered.connect(lambda: self.behavior.set_state("reviewing"))
        menu.addAction(act)

        menu.addSeparator()

        size_menu = menu.addMenu("尺寸")
        for label, scale in [
            ("50%", 0.5),
            ("75%", 0.75),
            ("100%", 1.0),
            ("150%", 1.5),
            ("200%", 2.0),
        ]:
            act = QAction(label, self)
            act.triggered.connect(lambda checked, s=scale: self.set_scale(s))
            size_menu.addAction(act)

        menu.addSeparator()

        quit_act = QAction("退出  ✕", self)
        quit_act.triggered.connect(self._quit)
        menu.addAction(quit_act)

        menu.popup(QCursor.pos())

    def _on_chat_submit(self, text: str) -> None:
        self.chat_input.hide()
        if not self.ai_engine or not self.ai_engine.is_available():
            self.speech_bubble.show_text(
                "（无法连接 AI）", self.pos(), self.size(), duration_ms=2000
            )
            return

        # Keyword-based action detection (fallback for AI tag)
        pre_action = self._detect_action(text)
        if pre_action:
            self.speech_bubble.show_text(pre_action, self.pos(), self.size(), duration_ms=4000)

        ctx = self._get_context()
        prompt = f"{text}\n（桌面状态：{ctx}）"
        self._waiting_for_reply = True
        self.speech_bubble.show_text("...", self.pos(), self.size(), duration_ms=0)
        self.ai_engine.send_message_async(prompt, self._on_ai_reply)

    def _detect_action(self, text: str) -> str | None:
        """Keyword-based action detection as fallback."""
        t = text.strip().lower()
        if any(kw in t for kw in ("放音乐", "听歌", "听音乐", "qq音乐", "打开qq音乐")):
            err = app_actions.open_app("QQ音乐")
            return f"好的，帮你打开QQ音乐~" if not err else err
        if any(kw in t for kw in ("网易云", "打开网易云")):
            err = app_actions.open_app("网易云音乐")
            return f"好的，帮你打开网易云~" if not err else err
        if any(kw in t for kw in ("记事本", "打开记事本")):
            err = app_actions.open_app("记事本")
            return f"好的~" if not err else err
        if any(kw in t for kw in ("计算器", "打开计算器")):
            err = app_actions.open_app("计算器")
            return f"好的~" if not err else err
        if any(kw in t for kw in ("浏览器", "打开浏览器")):
            err = app_actions.open_app("浏览器")
            return f"好的~" if not err else err
        return None

    def _execute_action(self, reply: str) -> str:
        """Extract and execute [ACTION:type:param] from reply. Returns cleaned text."""
        pattern = r"\[ACTION:(\w+):([^\]]+)\]"
        match = re.search(pattern, reply)
        if not match:
            return reply
        action_type = match.group(1)
        param = match.group(2).strip()

        if action_type == "open_app":
            err = app_actions.open_app(param)
            if err:
                return err
        elif action_type == "search":
            err = app_actions.search_web(param)
            if err:
                return err
        elif action_type == "open_url":
            err = app_actions.open_url(param)
            if err:
                return err

        return re.sub(pattern, "", reply).strip()

    def _on_ai_reply(self, reply: str) -> None:
        self._waiting_for_reply = False
        reply = self._execute_action(reply)
        if reply:
            self.speech_bubble.show_text(
                reply, self.pos(), self.size(), duration_ms=6000
            )

    def _quit(self) -> None:
        from PyQt6.QtWidgets import QApplication

        self.behavior.stop_auto_behavior()
        self.speech_bubble.close()
        self.chat_input.close()
        QApplication.quit()
