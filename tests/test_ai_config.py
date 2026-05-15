import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ai_config import get_api_key, get_model, get_base_url, get_max_history, AI_SETTINGS


class TestGetApiKey:
    def test_returns_env_var_when_set(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test123")
        assert get_api_key() == "sk-test123"

    def test_returns_none_when_not_set(self, monkeypatch):
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        assert get_api_key() is None


class TestGetModel:
    def test_returns_deepseek_model(self):
        assert get_model() == "deepseek-v4-pro"


class TestGetBaseUrl:
    def test_returns_default(self):
        assert get_base_url() == "https://api.deepseek.com"

    def test_returns_env_var_when_set(self, monkeypatch):
        monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://custom.api.com")
        assert get_base_url() == "https://custom.api.com"


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
