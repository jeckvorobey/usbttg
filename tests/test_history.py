"""Тесты для модуля хранения истории диалогов."""

import pytest
import pytest_asyncio

from ai.history import MessageHistory


@pytest_asyncio.fixture
async def history():
    """Создаёт экземпляр истории с in-memory базой данных."""
    h = MessageHistory(db_path=":memory:")
    await h.init_db()
    return h


async def test_save_and_get_message(history):
    """Проверяет сохранение одного сообщения и его получение по user_id."""
    await history.save_message(user_id=123, role="user", text="Привет!")
    messages = await history.get_history(user_id=123)

    assert len(messages) == 1
    assert messages[0]["text"] == "Привет!"
    assert messages[0]["role"] == "user"


async def test_get_history_isolation_by_user_id(history):
    """Проверяет, что история одного пользователя не смешивается с другим."""
    await history.save_message(user_id=111, role="user", text="Сообщение пользователя 111")
    await history.save_message(user_id=222, role="user", text="Сообщение пользователя 222")

    messages_111 = await history.get_history(user_id=111)
    messages_222 = await history.get_history(user_id=222)

    assert len(messages_111) == 1
    assert messages_111[0]["text"] == "Сообщение пользователя 111"
    assert len(messages_222) == 1
    assert messages_222[0]["text"] == "Сообщение пользователя 222"


async def test_history_limit(history):
    """Проверяет, что параметр limit ограничивает количество возвращаемых сообщений."""
    for i in range(10):
        await history.save_message(user_id=999, role="user", text=f"Сообщение {i}")

    messages = await history.get_history(user_id=999, limit=5)
    assert len(messages) == 5


async def test_history_save_assistant_role(history):
    """Проверяет сохранение сообщения с ролью 'assistant'."""
    await history.save_message(user_id=42, role="user", text="Вопрос")
    await history.save_message(user_id=42, role="assistant", text="Ответ")

    messages = await history.get_history(user_id=42)
    assert len(messages) == 2
    roles = [m["role"] for m in messages]
    assert "user" in roles
    assert "assistant" in roles


async def test_empty_history_returns_empty_list(history):
    """Проверяет, что запрос истории несуществующего пользователя возвращает пустой список."""
    messages = await history.get_history(user_id=99999)
    assert messages == []
