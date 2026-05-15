from __future__ import annotations

from openai import OpenAI

from PyQt6.QtCore import QThread, pyqtSignal

from ai_config import AI_SETTINGS, get_max_history, get_model, get_base_url


def build_messages(
    user_text: str,
    history: list[dict[str, str]],
    max_history: int | None = None,
) -> list[dict[str, str]]:
    if max_history is None:
        max_history = get_max_history()

    if len(history) > max_history:
        history = history[-max_history:]

    messages: list[dict[str, str]] = [
        {"role": "system", "content": AI_SETTINGS["system_prompt"]},
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    return messages


class ChatWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, api_key: str, base_url: str, model: str, messages: list[dict[str, str]], parent=None):
        super().__init__(parent)
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._messages = messages

    def run(self) -> None:
        try:
            client = OpenAI(api_key=self._api_key, base_url=self._base_url)
            response = client.chat.completions.create(
                model=self._model,
                max_tokens=150,
                messages=self._messages,
            )
            reply = response.choices[0].message.content
            self.finished.emit(reply)
        except Exception as e:
            self.finished.emit(f"（出错了：{e}）")


class AIEngine:
    def __init__(self, api_key: str | None) -> None:
        self.system_prompt: str = AI_SETTINGS["system_prompt"]
        self.history: list[dict[str, str]] = []
        self._api_key = api_key
        self._base_url = get_base_url()
        self._model = get_model()
        self._client: OpenAI | None = None

        if api_key is not None:
            self._client = OpenAI(api_key=api_key, base_url=self._base_url)

    def is_available(self) -> bool:
        return self._client is not None

    def send_message_async(self, user_text: str, on_reply) -> None:
        messages = build_messages(user_text=user_text, history=self.history)
        self.history.append({"role": "user", "content": user_text})

        self._worker = ChatWorker(
            api_key=self._api_key,
            base_url=self._base_url,
            model=self._model,
            messages=messages,
        )
        self._worker.finished.connect(
            lambda reply: self._on_reply(reply, on_reply)
        )
        self._worker.start()

    def _on_reply(self, reply: str, on_reply) -> None:
        self.history.append({"role": "assistant", "content": reply})
        max_entries = get_max_history() * 2
        if len(self.history) > max_entries:
            self.history = self.history[-max_entries:]
        on_reply(reply)
