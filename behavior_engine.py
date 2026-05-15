from __future__ import annotations

import math
import random
import time

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from animation_manager import AnimationManager

SPEED = 6
JUMP_HEIGHT = 10
JUMP_DURATION = 0.6  # seconds
TICK_MS = 30


class BehaviorEngine(QObject):
    move_by = pyqtSignal(int, int)

    auto_actions: tuple[str, ...] = (
        "running-left", "running-right", "waving", "jumping", "waiting"
    )
    reaction_states: tuple[str, ...] = (
        "running-left", "running-right", "jumping", "waving", "reviewing", "failed"
    )

    def __init__(
        self, animation_manager: AnimationManager, parent: QObject | None = None
    ) -> None:
        super().__init__(parent)
        self.anim: AnimationManager = animation_manager
        self.state: str = "idle"

        self._auto_timer = QTimer(self)
        self._auto_timer.timeout.connect(self._on_auto_tick)

        self._return_timer = QTimer(self)
        self._return_timer.setSingleShot(True)
        self._return_timer.timeout.connect(self._return_to_idle)

        self._move_timer = QTimer(self)
        self._move_timer.timeout.connect(self._on_move_tick)
        self._move_timer.start(TICK_MS)

        self._jump_start = 0.0
        self._jump_dx = 0

    def start_auto_behavior(self, min_ms: int = 5000, max_ms: int = 15000) -> None:
        self._schedule_next_auto(min_ms, max_ms)

    def stop_auto_behavior(self) -> None:
        self._auto_timer.stop()

    def _schedule_next_auto(self, min_ms: int, max_ms: int) -> None:
        interval = random.randint(min_ms, max_ms)
        self._auto_timer.start(interval)

    def _on_auto_tick(self) -> None:
        self._auto_timer.stop()
        self.do_random_action()
        self._schedule_next_auto(5000, 15000)

    def _on_move_tick(self) -> None:
        dx, dy = 0, 0

        if self.state == "running-left":
            dx = -SPEED
        elif self.state == "running-right":
            dx = SPEED
        elif self.state == "jumping":
            elapsed = time.time() - self._jump_start
            progress = elapsed / JUMP_DURATION
            if progress < 1.0:
                dy = int(-JUMP_HEIGHT * math.sin(progress * math.pi))
                dx = int(self._jump_dx * math.sin(progress * math.pi))
            else:
                dx, dy = 0, 0

        if dx != 0 or dy != 0:
            self.move_by.emit(dx, dy)

    def set_state(self, state: str) -> None:
        if state in self.anim.movies:
            self.state = state
            self.anim.switch_state(state)
        else:
            self.state = "idle"
            self.anim.switch_state("idle")

        if state == "jumping":
            self._jump_start = time.time()
            self._jump_dx = random.choice([-3, -1, 0, 1, 3])

    def flip_direction(self) -> None:
        """Reverse running direction — called when hitting screen edge."""
        if self.state == "running-left":
            self.set_state("running-right")
        elif self.state == "running-right":
            self.set_state("running-left")

    def do_random_action(self) -> None:
        action = random.choice(self.auto_actions)
        self.set_state(action)
        duration = 4000 if action.startswith("running") else 3000
        self._return_timer.start(duration)

    def react_to_click(self) -> None:
        reaction = random.choice(self.reaction_states)
        self.set_state(reaction)
        duration = 4000 if reaction.startswith("running") else 2500
        self._return_timer.start(duration)

    def react_to_double_click(self) -> None:
        self.set_state("jumping")
        self._return_timer.start(int(JUMP_DURATION * 1000) + 200)

    def _return_to_idle(self) -> None:
        self.set_state("idle")
