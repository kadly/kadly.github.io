# src/handlers/common.py

from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

import logging
from typing import Dict, List, Any # <-- Добавляем типизацию

# --- Импорты сервисов и утилит ---
from src.services.gemini import get_elder_text_response
from src.utils.message_splitter import edit_or_send_long_message
# --- Импортируем константу ---
from src.config import MAX_HISTORY_MESSAGES

router = Router(name="common-router")
logger = logging.getLogger(__name__)

# --- Хранилище Истории Диалогов (в памяти) ---
# Формат: {user_id: [{'role': 'user'/'model', 'parts': ['text']}, ...]}
user_histories: Dict[int, List[Dict[str, Any]]] = {}

# --- Хелпер для обновления истории ---
def update_history(user_id: int, user_message: str, bot_response: str):
    """Добавляет сообщения в историю и обрезает её до MAX_HISTORY_MESSAGES."""
    if user_id not in user_histories:
        user_histories[user_id] = []

    # Добавляем сообщение пользователя
    user_histories[user_id].append({"role": "user", "parts": [user_message]})
    # Добавляем ответ бота
    user_histories[user_id].append({"role": "model", "parts": [bot_response]})

    # Обрезаем историю, если она слишком длинная
    if len(user_histories[user_id]) > MAX_HISTORY_MESSAGES:
        # Удаляем самые старые сообщения (первые элементы списка)
        excess_count = len(user_histories[user_id]) - MAX_HISTORY_MESSAGES
        user_histories[user_id] = user_histories[user_id][excess_count:]
        logger.debug(f"История для user_id={user_id} обрезана, удалено {excess_count} старых сообщений.")

# --- Обработчики Команд ---

@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    # Очищаем историю при старте нового диалога (опционально)
    if user_id in user_histories:
        del user_histories[user_id]
        logger.info(f"История для user_id={user_id} очищена при /start.")

    await message.answer(
            "Здравствуйте! Я - виртуальный ассистент..."
            "Задайте мне вопрос о трейдинге... или отправьте график.\n\n"
            "Используйте /new_session, чтобы начать новый диалог (очистить память)." # Добавили подсказку
        )

@router.message(Command(commands=['help']))
async def cmd_help(message: Message):
     # await cmd_start(message) # Не лучший вариант, т.к. сбросит историю
     await message.answer( # Даем отдельное help-сообщение
            "Я - виртуальный ассистент по трейдингу в стиле доктора Элдера.\n\n"
            "- Задавайте вопросы о рынке, психологии, анализе.\n"
            "- Отправляйте скриншоты графиков для анализа.\n"
            "- Используйте команду `/quote <ТИКЕР>` для получения котировки с MOEX.\n"
            "- Используйте /new_session, чтобы начать новый диалог (очистить память).\n\n"
            "**Помните:** Я ИИ-симуляция, не даю фин. советов."
        )

# --- НОВАЯ КОМАНДА: Очистка истории ---
@router.message(Command(commands=['new_session', 'clear'], ignore_mention=True))
async def cmd_new_session(message: Message):
    """Очищает историю диалога для текущего пользователя."""
    user_id = message.from_user.id
    if user_id in user_histories:
        del user_histories[user_id]
        logger.info(f"История для user_id={user_id} очищена командой /new_session.")
        await message.reply("Хорошо, начнем с чистого листа. Задавайте ваш вопрос.")
    else:
        await message.reply("У нас еще не было диалога, память и так чиста.")


# --- Обработчик Текстовых Сообщений (ОБНОВЛЕННЫЙ) ---
@router.message(F.text)
async def handle_text(message: Message):
    """
    Обрабатывает текстовые сообщения пользователя, используя RAG и историю диалога.
    """
    user_id = message.from_user.id
    user_text = message.text
    if not user_text: return

    status_message = await message.reply("⏳ Анализирую ваш вопрос, обращаюсь к базе знаний и памяти...")

    # Получаем текущую историю для пользователя
    current_history = user_histories.get(user_id, [])
    logger.debug(f"Текущая длина истории для user_id={user_id}: {len(current_history)} сообщений.")

    response_text = "" # Инициализируем переменную для ответа
    try:
        # Вызываем функцию генерации текстового ответа, ПЕРЕДАВАЯ ИСТОРИЮ
        response_text = await get_elder_text_response(user_text, current_history)

        # Обновляем историю ТОЛЬКО ПОСЛЕ успешного получения ответа
        # Передаем оригинальный текст пользователя и полученный текст ответа
        update_history(user_id, user_text, response_text)
        logger.debug(f"История для user_id={user_id} обновлена.")

        # Отправляем ответ пользователю через сплиттер
        await edit_or_send_long_message(
            target_message=status_message,
            text=response_text,
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        logger.error(f"Критическая ошибка при обработке текстового сообщения user_id={user_id}: {e}", exc_info=True)
        # Не обновляем историю в случае ошибки
        try:
            await edit_or_send_long_message(
                 target_message=status_message,
                 text="❌ Произошла серьезная ошибка при обработке вашего вопроса. Попробуйте позже.",
                 parse_mode=None)
        except Exception as final_e:
            logger.error(f"Не удалось даже отправить сообщение об ошибке обработки текста: {final_e}")