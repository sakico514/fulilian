# 芙莉莲桌宠 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用 PyQt6 构建 Windows 桌面悬浮宠物，播放 GIF 动画，集成 Claude API 角色扮演对话。

**Architecture:** 9 个模块分工明确——主入口 `main.py`、悬浮窗 `pet_window.py`、动画管理 `animation_manager.py`、行为引擎 `behavior_engine.py`、交互处理 `interaction_handler.py`、AI 引擎 `ai_engine.py`、聊天气泡 `speech_bubble.py`、配置 `ai_config.py`、输入框 `chat_input.py`。按 TDD 流程：先写测试 → 再实现。

**Tech Stack:** Python 3.13, PyQt6, Anthropic Python SDK, pytest, python-dotenv

---

## File Structure

```
fulilian/
├── main.py                   # 入口
├── pet_window.py             # 悬浮窗容器
├── animation_manager.py      # GIF 加载与播放
├── behavior_engine.py        # 行为状态机
├── interaction_handler.py    # 鼠标事件处理
├── ai_engine.py              # Claude API
├── speech_bubble.py          # 聊天气泡
├── ai_config.py              # 配置管理
├── chat_input.py             # 对话输入框
├── assets/                   # GIF 文件目录
│   ├── idle.gif
│   ├── waving.gif
│   ├── running.gif
│   ├── running-left.gif
│   ├── running-right.gif
│   ├── jumping.gif
│   ├── waiting.gif
│   ├── review.gif
│   └── failed.gif
└── tests/
    ├── test_ai_config.py
    ├── test_animation_manager.py
    ├── test_behavior_engine.py
    └── test_ai_engine.py
```

---

### Task 1: 项目初始化与环境搭建

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: 移动 GIF 到 assets 目录**

```bash
cd d:\ai_agents\fulilian && mv *.gif assets/
```

- [ ] **Step 2: 写入 requirements.txt**

```txt
PyQt6>=6.7.0
anthropic>=0.40.0
python-dotenv>=1.0.0
pytest>=8.0.0
```

- [ ] **Step 3: 安装依赖**

```bash
cd d:\ai_agents\fulilian && pip install -r requirements.txt
```

- [ ] **Step 4: 验证安装**

```bash
python -c "from PyQt6.QtWidgets import QApplication; from anthropic import Anthropic; print('OK')"
```
Expected: `OK`

---

### Task 2: ai_config.py — 配置管理

**Files:**
- Create: `tests/test_ai_config.py`
- Create: `ai_config.py`

- [ ] **Step 1: 写测试 test_ai_config.py**

```python
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_config import get_api_key, get_model, get_max_history, AI_SETTINGS


class TestGetApiKey:
    def test_returns_env_var_when_set(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test123")
        assert get_api_key() == "sk-ant-test123"

    def test_returns_none_when_not_set(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        assert get_api_key() is None


class TestGetModel:
    def test_returns_default(self):
        assert get_model() == "claude-sonnet-4-6"


class TestGetMaxHistory:
    def test_returns_default_20(self):
        assert get_max_history() == 20


class TestAISettings:
    def test_all_settings_have_values(self):
        assert AI_SETTINGS["system_prompt"]
        assert "芙莉莲" in AI_SETTINGS["system_prompt"]
        assert AI_SETTINGS["max_history"] == 20
        assert AI_SETTINGS["auto_speak_min_sec"] == 300
        assert AI_SETTINGS["auto_speak_max_sec"] == 900
```

- [ ] **Step 2: Run test — 确认失败 (module not found)**

```bash
cd d:\ai_agents\fulilian && python -m pytest tests/test_ai_config.py -v
```
Expected: FAIL with `ModuleNotFoundError: No module named 'ai_config'`

- [ ] **Step 3: 实现 ai_config.py**

```python
import os

AI_SETTINGS = {
    "system_prompt": (
        "你是芙莉莲（Frieren），来自《葬送的芙莉莲》。"
        "你是一个活了一千多年的精灵魔法使，性格悠闲、天然呆、"
        "有点毒舌但内心温柔。你喜欢收集魔法，对一切感到好奇。\n\n"
        "说话风格：\n"
        "- 语气平淡、慵懒，偶尔带点挖苦\n"
        "- 提及过去时，喜欢引用'以前和勇者他们一起旅行的时候...'\n"
        "- 提到魔法时偶尔会眼睛发光\n"
        "- 每句话控制在 1-3 句，不啰嗦\n"
        "- 保持轻松、治愈的氛围\n\n"
        "现在你作为桌宠陪伴主人。用中文交流，不写动作描写，只说话。"
    ),
    "max_history": 20,
    "auto_speak_min_sec": 300,
    "auto_speak_max_sec": 900,
}


def get_api_key():
    return os.environ.get("ANTHROPIC_API_KEY")


def get_model():
    return "claude-sonnet-4-6"


def get_max_history():
    return AI_SETTINGS["max_history"]
```

- [ ] **Step 4: Run test — 确认通过**

```bash
cd d:\ai_agents\fulilian && python -m pytest tests/test_ai_config.py -v
```
Expected: PASS

---

### Task 3: animation_manager.py — 动画管理

**Files:**
- Create: `tests/test_animation_manager.py`
- Create: `animation_manager.py`

- [ ] **Step 1: 写测试 test_animation_manager.py**

```python
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from animation_manager import AnimationManager, STATE_GIF_MAP


class TestStateGifMap:
    def test_has_nine_states(self):
        assert len(STATE_GIF_MAP) == 9

    def test_idle_mapped(self):
        assert STATE_GIF_MAP["idle"] == "idle.gif"

    def test_all_states_end_with_gif(self):
        for state, filename in STATE_GIF_MAP.items():
            assert filename.endswith(".gif"), f"{state} -> {filename}"


class TestAnimationManager:
    @pytest.fixture
    def assets_dir(self, tmp_path):
        d = tmp_path / "assets"
        d.mkdir()
        for name in ["idle.gif", "running.gif", "jumping.gif",
                     "waving.gif", "waiting.gif", "failed.gif",
                     "review.gif", "running-left.gif", "running-right.gif"]:
            (d / name).write_bytes(b"GIF89a\x00\x00\x00\x00;")
        return str(d)

    def test_load_all_gifs_success(self, assets_dir):
        mgr = AnimationManager(assets_dir)
        mgr.load_all()
        assert len(mgr.movies) == 9
        assert "idle" in mgr.movies

    def test_load_missing_gif_skips(self, assets_dir):
        import os
        os.remove(os.path.join(assets_dir, "failed.gif"))
        mgr = AnimationManager(assets_dir)
        mgr.load_all()
        assert "failed" not in mgr.movies
        assert len(mgr.movies) == 8

    def test_current_state_starts_none(self, assets_dir):
        mgr = AnimationManager(assets_dir)
        assert mgr.current_state is None

    def test_switch_state_updates_current(self, assets_dir):
        mgr = AnimationManager(assets_dir)
        mgr.load_all()
        mgr.switch_state("jumping")
        assert mgr.current_state == "jumping"
```

- [ ] **Step 2: Run test — 确认失败**

```bash
cd d:\ai_agents\fulilian && python -m pytest tests/test_animation_manager.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现 animation_manager.py**

```python
import os
from PyQt6.QtCore import QObject
from PyQt6.QtGui import QMovie

STATE_GIF_MAP = {
    "idle": "idle.gif",
    "running": "running.gif",
    "running-left": "running-left.gif",
    "running-right": "running-right.gif",
    "jumping": "jumping.gif",
    "waving": "waving.gif",
    "waiting": "waiting.gif",
    "failed": "failed.gif",
    "reviewing": "review.gif",
}


class AnimationManager(QObject):
    def __init__(self, assets_dir, parent=None):
        super().__init__(parent)
        self.assets_dir = assets_dir
        self.movies = {}
        self.current_state = None
        self._label = None

    def set_label(self, label):
        self._label = label

    def load_all(self):
        for state, filename in STATE_GIF_MAP.items():
            path = os.path.join(self.assets_dir, filename)
            if os.path.exists(path):
                movie = QMovie(path)
                movie.setCacheMode(QMovie.CacheMode.CacheAll)
                self.movies[state] = movie

    def switch_state(self, state):
        if state not in self.movies:
            return
        if self._label is None:
            return
        self.current_state = state
        movie = self.movies[state]
        self._label.setMovie(movie)
        movie.start()
```

- [ ] **Step 4: Run test — 确认通过**

```bash
cd d:\ai_agents\fulilian && python -m pytest tests/test_animation_manager.py -v
```
Expected: PASS

---

### Task 4: behavior_engine.py — 行为状态机

**Files:**
- Create: `tests/test_behavior_engine.py`
- Create: `behavior_engine.py`

- [ ] **Step 1: 写测试 test_behavior_engine.py**

```python
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from behavior_engine import BehaviorEngine


class FakeAnimManager:
    def __init__(self):
        self.last_state = None
        self.movies = {s: True for s in [
            "idle", "running", "running-left", "running-right",
            "jumping", "waving", "waiting", "failed", "reviewing"
        ]}

    def switch_state(self, state):
        self.last_state = state


class TestBehaviorEngine:
    @pytest.fixture
    def engine(self):
        anim = FakeAnimManager()
        return BehaviorEngine(anim)

    def test_initial_state_is_idle(self, engine):
        assert engine.state == "idle"

    def test_set_state_switches_animation(self, engine):
        engine.set_state("jumping")
        assert engine.state == "jumping"
        assert engine.anim.last_state == "jumping"

    def test_set_state_unknown_falls_back(self, engine):
        engine.set_state("nonexistent")
        assert engine.state == "idle"

    def test_do_random_action_changes_state(self, engine):
        engine.set_state("idle")
        engine.do_random_action()
        assert engine.state != "idle" or engine.state == "idle"

    def test_react_to_click_returns_to_idle(self, engine):
        engine.react_to_click()
        assert engine.state in engine.reaction_states
        engine.set_state("idle")

    def test_react_to_double_click_is_jumping(self, engine):
        engine.react_to_double_click()
        assert engine.state == "jumping"

    def test_auto_actions_are_subset(self, engine):
        for s in engine.auto_actions:
            assert s in ("running-left", "running-right", "waving", "jumping", "waiting")

    def test_reaction_states_are_subset(self, engine):
        for s in engine.reaction_states:
            assert s in ("jumping", "waving", "reviewing", "failed")
```

- [ ] **Step 2: Run test — 确认失败**

```bash
cd d:\ai_agents\fulilian && python -m pytest tests/test_behavior_engine.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现 behavior_engine.py**

```python
import random
from PyQt6.QtCore import QObject, QTimer


class BehaviorEngine(QObject):
    auto_actions = ("running-left", "running-right", "waving", "jumping", "waiting")
    reaction_states = ("jumping", "waving", "reviewing", "failed")

    def __init__(self, animation_manager, parent=None):
        super().__init__(parent)
        self.anim = animation_manager
        self.state = "idle"
        self._auto_timer = QTimer(self)
        self._auto_timer.timeout.connect(self._on_auto_tick)
        self._return_timer = QTimer(self)
        self._return_timer.setSingleShot(True)
        self._return_timer.timeout.connect(self._return_to_idle)

    def start_auto_behavior(self, min_ms=5000, max_ms=15000):
        self._schedule_next_auto(min_ms, max_ms)

    def stop_auto_behavior(self):
        self._auto_timer.stop()

    def _schedule_next_auto(self, min_ms, max_ms):
        interval = random.randint(min_ms, max_ms)
        self._auto_timer.start(interval)

    def _on_auto_tick(self):
        self._auto_timer.stop()
        self.do_random_action()
        self._schedule_next_auto(5000, 15000)

    def set_state(self, state):
        if state in self.anim.movies:
            self.state = state
            self.anim.switch_state(state)
        else:
            self.state = "idle"
            self.anim.switch_state("idle")

    def do_random_action(self):
        action = random.choice(self.auto_actions)
        self.set_state(action)
        self._return_timer.start(3000)

    def react_to_click(self):
        reaction = random.choice(self.reaction_states)
        self.set_state(reaction)
        self._return_timer.start(2500)

    def react_to_double_click(self):
        self.set_state("jumping")
        self._return_timer.start(2000)

    def _return_to_idle(self):
        self.set_state("idle")
```

- [ ] **Step 4: Run test — 确认通过**

```bash
cd d:\ai_agents\fulilian && python -m pytest tests/test_behavior_engine.py -v
```
Expected: PASS

---

### Task 5: ai_engine.py — Claude API 调用

**Files:**
- Create: `tests/test_ai_engine.py`
- Create: `ai_engine.py`

- [ ] **Step 1: 写测试 test_ai_engine.py**

```python
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from ai_engine import AIEngine, build_messages


class TestBuildMessages:
    def test_empty_history(self):
        msgs = build_messages("你好", [])
        assert len(msgs) == 2
        assert msgs[0]["role"] == "user"
        assert msgs[1]["role"] == "user"
        assert msgs[1]["content"] == "你好"

    def test_with_history(self):
        history = [
            {"role": "user", "content": "你是谁"},
            {"role": "assistant", "content": "芙莉莲"},
        ]
        msgs = build_messages("你好", history)
        assert len(msgs) == 4
        assert msgs[2]["role"] == "user"
        assert msgs[2]["content"] == "你是谁"

    def test_truncates_history(self):
        history = [{"role": "user", "content": str(i)} for i in range(50)]
        msgs = build_messages("hey", history, max_history=6)
        assert len(msgs) == 8  # system + 6 history + 1 new user


class TestAIEngine:
    @pytest.fixture
    def engine(self):
        return AIEngine(api_key="fake-key")

    def test_has_system_prompt(self, engine):
        assert "芙莉莲" in engine.system_prompt

    def test_is_available_with_key(self, engine):
        assert engine.is_available() is True

    def test_is_not_available_without_key(self):
        engine = AIEngine(api_key=None)
        assert engine.is_available() is False
```

- [ ] **Step 2: Run test — 确认失败**

```bash
cd d:\ai_agents\fulilian && python -m pytest tests/test_ai_engine.py -v
```
Expected: FAIL

- [ ] **Step 3: 实现 ai_engine.py**

```python
from anthropic import Anthropic
from ai_config import AI_SETTINGS


def build_messages(user_text, history, max_history=None):
    if max_history is None:
        max_history = AI_SETTINGS["max_history"]
    recent = history[-(max_history * 2):]
    system_msg = {
        "role": "user",
        "content": AI_SETTINGS["system_prompt"],
    }
    return [system_msg] + recent + [{"role": "user", "content": user_text}]


class AIEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.system_prompt = AI_SETTINGS["system_prompt"]
        self.history = []
        self._client = Anthropic(api_key=api_key) if api_key else None

    def is_available(self):
        return self._client is not None

    def send_message(self, user_text):
        if not self._client:
            return None
        messages = build_messages(user_text, self.history)
        response = self._client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=150,
            messages=messages,
        )
        reply = response.content[0].text
        self.history.append({"role": "user", "content": user_text})
        self.history.append({"role": "assistant", "content": reply})
        if len(self.history) > AI_SETTINGS["max_history"] * 2:
            self.history = self.history[-(AI_SETTINGS["max_history"] * 2):]
        return reply
```

- [ ] **Step 4: Run test — 确认通过**

```bash
cd d:\ai_agents\fulilian && python -m pytest tests/test_ai_engine.py -v
```
Expected: PASS

---

### Task 6: speech_bubble.py — 聊天气泡

**Files:**
- Create: `speech_bubble.py`

- [ ] **Step 1: 实现 speech_bubble.py**

```python
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from PyQt6.QtGui import QFont


class SpeechBubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(260)
        self.label.setFont(QFont("Microsoft YaHei", 11))
        font = self.label.font()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 230);
                border: 1px solid #d0d0d0;
                border-radius: 12px;
                padding: 10px 14px;
                color: #333;
            }
        """)
        layout.addWidget(self.label)
        self.adjustSize()

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.fade_out)

    def show_text(self, text, owner_pos, owner_size, duration_ms=5000):
        self.label.setText(text)
        self.adjustSize()
        x = owner_pos.x() + owner_size.width() // 2 - self.width() // 2
        y = owner_pos.y() - self.height() - 10
        self.move(max(0, x), max(0, y))
        self.show()
        self._hide_timer.start(duration_ms)

    def fade_out(self):
        self.hide()
```

---

### Task 7: chat_input.py — 对话输入框

**Files:**
- Create: `chat_input.py`

- [ ] **Step 1: 实现 chat_input.py**

```python
from PyQt6.QtWidgets import QWidget, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal


class ChatInput(QWidget):
    submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.input = QLineEdit(self)
        self.input.setPlaceholderText("和芙莉莲说点什么...")
        self.input.setMinimumWidth(240)
        self.input.setFont(self.input.font())
        font = self.input.font()
        font.setPointSize(11)
        self.input.setFont(font)
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 235);
                border: 1px solid #c0c0c0;
                border-radius: 8px;
                padding: 6px 10px;
            }
        """)
        self.input.returnPressed.connect(self._on_submit)
        layout.addWidget(self.input)
        self.adjustSize()

    def _on_submit(self):
        text = self.input.text().strip()
        if text:
            self.submitted.emit(text)
            self.input.clear()

    def show_at(self, pos, owner_size):
        x = pos.x() + owner_size.width() // 2 - self.width() // 2
        y = pos.y() + owner_size.height() + 6
        self.move(max(0, x), max(0, y))
        self.show()
        self.input.setFocus()
```

---

### Task 8: pet_window.py + main.py — 悬浮窗与主入口

**Files:**
- Create: `pet_window.py`
- Create: `interaction_handler.py`
- Create: `main.py`

- [ ] **Step 1: 实现 interaction_handler.py**

```python
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject


class InteractionHandler(QObject):
    clicked = pyqtSignal()
    double_clicked = pyqtSignal()
    right_clicked = pyqtSignal(QPoint)

    def __init__(self, parent_window):
        super().__init__(parent_window)
        self._window = parent_window
        self._drag_pos = None

    def handle_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_clicked.emit(event.globalPosition().toPoint())

    def handle_mouse_move(self, event):
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._window.move(self._window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def handle_mouse_release(self, event):
        if self._drag_pos is None:
            return
        total_delta = event.globalPosition().toPoint() - self._drag_pos
        if total_delta.manhattanLength()() < 5:
            self.clicked.emit()
        self._drag_pos = None

    def handle_mouse_double_click(self, event):
        self.double_clicked.emit()
```

- [ ] **Step 2: 修复 interaction_handler.py 的 bug — manhattanLength 不是 callable**

`manhattanLength()` 是属性不是方法，修正为：

```python
    def handle_mouse_release(self, event):
        if self._drag_pos is None:
            return
        delta = event.globalPosition().toPoint() - self._drag_pos
        if delta.manhattanLength() < 5:
            self.clicked.emit()
        self._drag_pos = None
```

- [ ] **Step 3: 实现 pet_window.py**

```python
import os
from PyQt6.QtWidgets import QWidget, QLabel, QMenu
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QCursor

from animation_manager import AnimationManager
from behavior_engine import BehaviorEngine
from interaction_handler import InteractionHandler
from speech_bubble import SpeechBubble
from chat_input import ChatInput
from ai_engine import AIEngine
from ai_config import get_api_key


class PetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.label = QLabel(self)
        self.label.setStyleSheet("background: transparent;")

        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        self.anim_manager = AnimationManager(assets_dir, self)
        self.anim_manager.load_all()

        first_movie = self.anim_manager.movies.get("idle")
        if first_movie:
            size = first_movie.currentPixmap().size()
            self.label.setFixedSize(size)
            self.setFixedSize(size)

        self.anim_manager.set_label(self.label)
        self.anim_manager.switch_state("idle")

        self.behavior = BehaviorEngine(self.anim_manager, self)
        self.behavior.start_auto_behavior(5000, 15000)
        self.behavior._return_to_idle = self._on_return_to_idle

        self.interaction = InteractionHandler(self)
        self.interaction.clicked.connect(self._on_click)
        self.interaction.double_clicked.connect(self._on_double_click)
        self.interaction.right_clicked.connect(self._on_right_click)

        api_key = get_api_key()
        self.ai_engine = AIEngine(api_key) if api_key else None
        self._conversation_history = []

        self.speech_bubble = SpeechBubble()
        self.chat_input = ChatInput()
        self.chat_input.submitted.connect(self._on_chat_submit)

        self._auto_speak_timer = QTimer(self)
        self._auto_speak_timer.timeout.connect(self._auto_speak)
        self._schedule_auto_speak()

    def _schedule_auto_speak(self):
        import random
        from ai_config import AI_SETTINGS
        sec = random.randint(
            AI_SETTINGS["auto_speak_min_sec"],
            AI_SETTINGS["auto_speak_max_sec"],
        )
        self._auto_speak_timer.start(sec * 1000)

    def _auto_speak(self):
        self._auto_speak_timer.stop()
        if self.ai_engine and self.ai_engine.is_available():
            prompts = [
                "（自言自语）随便说点什么，作为桌宠，1-2句就行",
            ]
            import random
            prompt = random.choice(prompts)
            reply = self.ai_engine.send_message(prompt)
            if reply:
                self.speech_bubble.show_text(
                    reply, self.pos(), self.size(), duration_ms=5000
                )
        self._schedule_auto_speak()

    def mousePressEvent(self, event):
        self.interaction.handle_mouse_press(event)

    def mouseMoveEvent(self, event):
        self.interaction.handle_mouse_move(event)

    def mouseReleaseEvent(self, event):
        self.interaction.handle_mouse_release(event)
        # Also track original press position for double-click
        if not hasattr(self, '_press_pos'):
            self._press_pos = None

    def mouseDoubleClickEvent(self, event):
        self.interaction.handle_mouse_double_click(event)

    def _on_click(self):
        self.behavior.react_to_click()
        self.chat_input.show_at(self.pos(), self.size())

    def _on_double_click(self):
        self.behavior.react_to_double_click()
        self.chat_input.show_at(self.pos(), self.size())

    def _on_right_click(self, pos):
        menu = QMenu(self)
        actions = [
            ("待机", "idle"),
            ("挥手", "waving"),
            ("跳跃", "jumping"),
            ("走动", "running"),
            ("审视", "reviewing"),
        ]
        for name, state in actions:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, s=state: self.behavior.set_state(s))
            menu.addAction(action)
        menu.addSeparator()
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self._quit)
        menu.addAction(quit_action)
        menu.exec(QCursor.pos())

    def _on_chat_submit(self, text):
        self.chat_input.hide()
        if not self.ai_engine or not self.ai_engine.is_available():
            self.speech_bubble.show_text(
                "...", self.pos(), self.size(), duration_ms=2000
            )
            return
        reply = self.ai_engine.send_message(text)
        if reply:
            self.speech_bubble.show_text(
                reply, self.pos(), self.size(), duration_ms=6000
            )

    def _on_return_to_idle(self):
        self.behavior.set_state("idle")

    def _quit(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()
```

- [ ] **Step 4: 实现 main.py**

```python
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


def main():
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    from pet_window import PetWindow
    pet = PetWindow()
    pet.move(100, 100)
    pet.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

### Task 9: 集成测试与运行验证

- [ ] **Step 1: 移动 GIF 到 assets 目录（若未完成）**

```bash
cd d:\ai_agents\fulilian && for f in *.gif; do mv "$f" assets/; done
```

- [ ] **Step 2: 运行所有单元测试**

```bash
cd d:\ai_agents\fulilian && python -m pytest tests/ -v
```
Expected: 所有测试 PASS

- [ ] **Step 3: 手动验证 — 启动桌宠**

```bash
cd d:\ai_agents\fulilian && python main.py
```

手动检查清单:
- [ ] 宠物窗口出现在屏幕上，无边框、透明背景
- [ ] idle.gif 正在播放
- [ ] 可以拖拽宠物到屏幕其他位置
- [ ] 点击弹出输入框
- [ ] 右键弹出菜单
- [ ] 宠物定时自动切换动作

---

### Task 10: 修复与抛光

手动验证中发现的常见问题修复：

- [ ] **Step 1: 鼠标穿透 — 确保窗口接收鼠标事件**

如果宠物区域无法点击，在 `pet_window.py` 的 `__init__` 中确保：

```python
# 确保在 __init__ 最后
self.setMouseTracking(True)
```

- [ ] **Step 2: 检查 interaction_handler 点击检测逻辑**

确保 `mouseReleaseEvent` 中的 `_drag_pos` 在 `mousePressEvent` 中正确设置。修复 interaction_handler 中的引用问题：`handle_mouse_release` 接收 `event` 参数用于计算总位移，但 `_drag_pos` 在拖拽过程中通过 `handle_mouse_move` 不断更新，松手时 `_drag_pos` 已经是最终位置。需要保存初始按下位置：

修正 `interaction_handler.py`:

```python
class InteractionHandler(QObject):
    clicked = pyqtSignal()
    double_clicked = pyqtSignal()
    right_clicked = pyqtSignal(QPoint)

    def __init__(self, parent_window):
        super().__init__(parent_window)
        self._window = parent_window
        self._drag_pos = None
        self._press_pos = None

    def handle_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.globalPosition().toPoint()
            self._drag_pos = event.globalPosition().toPoint()
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_clicked.emit(event.globalPosition().toPoint())

    def handle_mouse_move(self, event):
        if self._drag_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self._window.move(self._window.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()

    def handle_mouse_release(self, event):
        if self._press_pos is not None:
            total = event.globalPosition().toPoint() - self._press_pos
            if total.manhattanLength() < 5:
                self.clicked.emit()
        self._drag_pos = None
        self._press_pos = None

    def handle_mouse_double_click(self, event):
        self.double_clicked.emit()
```
