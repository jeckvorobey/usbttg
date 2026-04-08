"""Инициализация и управление Telethon клиентом."""

from typing import Any


class UserBotClient:
    """Управляет подключением к Telegram через Telethon MTProto."""

    def __init__(self, session_name: str, api_id: int, api_hash: str) -> None:
        """
        Инициализирует Telethon клиент.

        Args:
            session_name: Имя файла сессии (без расширения .session).
            api_id: Telegram API ID (получить на https://my.telegram.org).
            api_hash: Telegram API Hash.
        """
        self.session_name = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self._client: Any | None = None

    async def start(self) -> None:
        """Запускает клиент и устанавливает подключение к Telegram."""
        if self._client is None:
            self._client = _build_telegram_client(
                self.session_name,
                self.api_id,
                self.api_hash,
            )
        await self._client.start()

    async def stop(self) -> None:
        """Корректно останавливает клиент и разрывает соединение."""
        if self._client is None:
            return
        if not self._client.is_connected():
            return
        await self._client.disconnect()

    @property
    def client(self) -> Any | None:
        """Возвращает внутренний экземпляр Telethon-клиента."""
        return self._client


def _build_telegram_client(session_name: str, api_id: int, api_hash: str) -> Any:
    """Создаёт экземпляр TelegramClient с ленивым импортом Telethon."""
    try:
        from telethon import TelegramClient
    except ImportError as exc:
        raise RuntimeError("Пакет telethon не установлен") from exc

    return TelegramClient(session_name, api_id, api_hash)
