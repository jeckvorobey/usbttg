"""Тесты для модуля Gemini AI клиента и загрузчика промтов."""

import tempfile
from pathlib import Path

import pytest

from ai.gemini import GeminiClient, PromptLoader


async def test_prompt_loader_reads_md_file():
    """Проверяет, что загрузчик читает содержимое .md файла по имени."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prompt_file = Path(tmpdir) / "system.md"
        prompt_file.write_text("Ты полезный ассистент.", encoding="utf-8")

        loader = PromptLoader(prompts_dir=tmpdir)
        content = await loader.load("system")

        assert "Ты полезный ассистент" in content


async def test_prompt_loader_raises_on_missing_file():
    """Проверяет, что FileNotFoundError бросается при отсутствии файла."""
    with tempfile.TemporaryDirectory() as tmpdir:
        loader = PromptLoader(prompts_dir=tmpdir)

        with pytest.raises(FileNotFoundError):
            await loader.load("несуществующий_промт")


async def test_prompt_loader_preserves_full_content():
    """Проверяет, что загрузчик возвращает полное содержимое файла."""
    content = "# Заголовок\n\nПервый абзац.\nВторой абзац."
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "test.md").write_text(content, encoding="utf-8")

        loader = PromptLoader(prompts_dir=tmpdir)
        result = await loader.load("test")

        assert result == content


def test_gemini_client_initializes_with_api_key():
    """Проверяет, что GeminiClient инициализируется и хранит имя модели."""
    client = GeminiClient(api_key="test_key_123", model_name="gemini-1.5-flash")
    assert client.model_name == "gemini-1.5-flash"


def test_gemini_client_default_model():
    """Проверяет дефолтное имя модели при инициализации."""
    client = GeminiClient(api_key="test_key_123")
    assert client.model_name is not None
    assert len(client.model_name) > 0
