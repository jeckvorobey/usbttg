"""Клиент Gemini AI и загрузчик промтов из .md файлов."""

import asyncio
from pathlib import Path
from typing import Any


class PromptLoader:
    """Загружает промты из .md файлов в runtime. Промты никогда не хардкодятся в коде."""

    def __init__(self, prompts_dir: str) -> None:
        """
        Инициализирует загрузчик промтов.

        Args:
            prompts_dir: Путь к директории, содержащей .md файлы промтов.
        """
        self.prompts_dir = prompts_dir

    async def load(self, name: str) -> str:
        """
        Загружает содержимое файла {name}.md из директории промтов.

        Args:
            name: Имя промта — имя файла без расширения .md.

        Returns:
            Полное текстовое содержимое файла промта.

        Raises:
            FileNotFoundError: Если файл {name}.md не найден в директории промтов.
        """
        path = Path(self.prompts_dir) / f"{name}.md"
        if not path.exists():
            raise FileNotFoundError(path)
        return await asyncio.to_thread(path.read_text, encoding="utf-8")


class GeminiClient:
    """Клиент для генерации ответов через Google Gemini API."""

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash") -> None:
        """
        Инициализирует клиент Gemini.

        Args:
            api_key: API ключ для доступа к Gemini.
            model_name: Название модели Gemini для генерации.
        """
        self.api_key = api_key
        self.model_name = model_name
        self._model: Any | None = None
        self._system_prompt: str | None = None

    async def generate_reply(
        self,
        system_prompt: str,
        history: list[dict[str, Any]],
        user_message: str,
    ) -> str:
        """
        Генерирует ответ на сообщение пользователя с учётом истории диалога.

        Args:
            system_prompt: Системный промт, задающий роль и поведение.
            history: История предыдущих сообщений (список словарей role/text).
            user_message: Текущее сообщение пользователя.

        Returns:
            Сгенерированный текстовый ответ.
        """
        prompt_parts = [self._render_history(history), f"Пользователь: {user_message}"]
        prompt = "\n\n".join(part for part in prompt_parts if part)
        return await self._generate_text(system_prompt=system_prompt, prompt=prompt)

    async def start_topic(self, system_prompt: str, topic: str) -> str:
        """
        Генерирует начальное сообщение для инициирования разговора на заданную тему.

        Args:
            system_prompt: Системный промт, задающий роль и поведение.
            topic: Тема разговора из списка тем.

        Returns:
            Начальное сообщение для старта разговора.
        """
        prompt = f"Тема разговора: {topic}"
        return await self._generate_text(system_prompt=system_prompt, prompt=prompt)

    async def _generate_text(self, system_prompt: str, prompt: str) -> str:
        """Выполняет один вызов модели и нормализует ответ."""
        model = self._get_model(system_prompt=system_prompt)
        response = await asyncio.to_thread(model.generate_content, prompt)
        text = getattr(response, "text", "")
        return str(text).strip()

    def _get_model(self, system_prompt: str) -> Any:
        """Ленивая инициализация Gemini-модели."""
        if self._model is None or self._system_prompt != system_prompt:
            try:
                import google.generativeai as genai
            except ImportError as exc:
                raise RuntimeError("Пакет google-generativeai не установлен") from exc

            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_prompt,
            )
            self._system_prompt = system_prompt
        return self._model

    @staticmethod
    def _render_history(history: list[dict[str, Any]]) -> str:
        """Преобразует историю диалога в текстовую форму для модели."""
        if not history:
            return ""

        rendered_messages = []
        for item in history:
            role = item.get("role", "user")
            text = item.get("text", "")
            rendered_messages.append(f"{role}: {text}")
        return "История диалога:\n" + "\n".join(rendered_messages)
