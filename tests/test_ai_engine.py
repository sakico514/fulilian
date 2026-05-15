import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from ai_engine import AIEngine, build_messages


class TestBuildMessages:
    def test_empty_history(self) -> None:
        msgs = build_messages("你好", [])
        assert len(msgs) == 2
        assert msgs[0]["role"] == "system"
        assert msgs[1]["role"] == "user"
        assert msgs[1]["content"] == "你好"

    def test_with_history(self) -> None:
        history = [
            {"role": "user", "content": "你是谁"},
            {"role": "assistant", "content": "芙莉莲"},
        ]
        msgs = build_messages("你好", history)
        assert len(msgs) == 4
        assert msgs[1]["role"] == "user"
        assert msgs[1]["content"] == "你是谁"

    def test_truncates_history(self) -> None:
        history = [{"role": "user", "content": str(i)} for i in range(50)]
        msgs = build_messages("hey", history, max_history=6)
        assert len(msgs) == 8


class TestAIEngine:
    @pytest.fixture
    def engine(self) -> AIEngine:
        return AIEngine(api_key="fake-key")

    def test_has_system_prompt(self, engine: AIEngine) -> None:
        assert "芙莉莲" in engine.system_prompt

    def test_is_available_with_key(self, engine: AIEngine) -> None:
        assert engine.is_available() is True

    def test_is_not_available_without_key(self) -> None:
        engine = AIEngine(api_key=None)
        assert engine.is_available() is False

    def test_send_message_async_no_crash(self) -> None:
        engine = AIEngine(api_key=None)
        # Should not raise — starts worker thread silently
        engine.send_message_async("hello", lambda r: None)
        assert engine.history[-1]["role"] == "user"
        assert engine.history[-1]["content"] == "hello"
