"""Настройки приложения, загружаемые из .env файла через pydantic-settings."""

from functools import lru_cache
from typing import Annotated

from pydantic import BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _empty_str_to_none(v: object) -> object:
    """Преобразует пустую строку в None — для необязательных числовых полей."""
    if isinstance(v, str) and v.strip() == "":
        return None
    return v


OptionalInt = Annotated[int | None, BeforeValidator(_empty_str_to_none)]


class Settings(BaseSettings):
    """Конфигурация userbot'а. Все поля читаются из переменных окружения или .env файла."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram API (получить на https://my.telegram.org)
    api_id: int
    api_hash: str

    # Gemini API (получить на https://aistudio.google.com)
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    gemini_fallback_model: str | None = "gemini-2.5-flash-lite"
    gemini_max_retries: int = 3
    gemini_retry_backoff_seconds: float = 1.0
    gemini_retry_jitter_seconds: float = 0.3

    # Telethon сессия (имя файла без .session)
    session_name: str = "84523248603"

    # Общий proxy URL для внешних подключений
    proxy_url: str | None = None

    # Уровень логирования приложения
    log_level: str = "INFO"

    # Пути к файлам данных
    db_path: str = "data/history.db"
    whitelist_path: str = "data/whitelist.md"
    topics_path: str = "data/topics.md"
    prompts_dir: str = "ai/prompts"

    # Планировщик разговоров
    scheduler_enabled: bool = True
    silence_timeout_minutes: int = 60
    group_chat_id: OptionalInt = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Возвращает единственный экземпляр настроек приложения.

    Returns:
        Инициализированный объект Settings.
    """
    return Settings()
