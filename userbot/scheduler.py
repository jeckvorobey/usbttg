"""Планировщик задач APScheduler и логика 30-минутных сессий разговора."""

from datetime import datetime
import asyncio
import random
from pathlib import Path


class TopicSelector:
    """Выбирает случайную тему для разговора из файла тем."""

    def __init__(self, topics_path: str) -> None:
        """
        Инициализирует селектор тем.

        Args:
            topics_path: Путь к файлу topics.md со списком тем.
        """
        self.topics_path = topics_path
        self.topics: list[str] = []

    async def load(self) -> None:
        """
        Загружает список тем из файла.

        Строки начинающиеся на '#' считаются комментариями и игнорируются.
        Пустые строки также игнорируются.
        """
        path = Path(self.topics_path)
        content = await asyncio.to_thread(path.read_text, encoding="utf-8")
        lines = [line.strip() for line in content.splitlines()]

        if "---" in lines:
            lines = lines[lines.index("---") + 1 :]

        self.topics = [
            line for line in lines if line and not line.startswith("#") and line != "---"
        ]

    async def pick_random(self) -> str:
        """
        Выбирает случайную тему из загруженного списка.

        Returns:
            Строка с темой разговора.

        Raises:
            ValueError: Если список тем пуст (с сообщением 'Список тем пуст').
        """
        if not self.topics:
            raise ValueError("Список тем пуст")
        return random.choice(self.topics)


class ConversationSession:
    """Управляет сессией разговора на одну тему с ограниченной длительностью."""

    def __init__(self, duration_minutes: int = 30) -> None:
        """
        Инициализирует сессию разговора.

        Args:
            duration_minutes: Длительность сессии в минутах (по умолчанию 30).
        """
        self.duration_minutes = duration_minutes
        self.current_topic: str | None = None
        self._start_time: datetime | None = None
        self._active: bool = False

    def start(self, topic: str) -> None:
        """
        Запускает сессию на заданную тему.

        Args:
            topic: Тема разговора для данной сессии.
        """
        self.current_topic = topic
        self._start_time = datetime.now()
        self._active = True

    def stop(self) -> None:
        """Досрочно останавливает текущую сессию."""
        self.current_topic = None
        self._start_time = None
        self._active = False

    def is_active(self) -> bool:
        """
        Проверяет, активна ли сессия (запущена и не истекла по времени).

        Returns:
            True если сессия активна, иначе False.
        """
        if not self._active or self._start_time is None:
            return False

        elapsed_seconds = (datetime.now() - self._start_time).total_seconds()
        if elapsed_seconds >= self.duration_minutes * 60:
            self.stop()
            return False
        return True
