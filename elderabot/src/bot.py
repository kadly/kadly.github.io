# src/bot.py
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# Импортируем конфигурацию (токен)
from src.config import TELEGRAM_BOT_TOKEN
# Импортируем все роутеры из папки handlers
from src.handlers import common, image_analysis, quote
from src.handlers import common, image_analysis, quote, journal

async def main():
    """Основная асинхронная функция для настройки и запуска бота."""
    # Настройка бота с токеном и параметрами по умолчанию (Markdown)
    bot = Bot(
        token=TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    # Используем простое хранилище FSM в памяти (пока не используется, но стандартно)
    storage = MemoryStorage()
    # Создаем диспетчер
    dp = Dispatcher(storage=storage)

    # --- ПРАВИЛЬНЫЙ ПОРЯДОК РЕГИСТРАЦИИ РОУТЕРОВ ---
    logging.info("Включение роутеров...")
    # 1. Сначала самые специфичные команды и типы контента
    dp.include_router(quote.router)         # Обработчик команды /quote
    dp.include_router(image_analysis.router) # Обработчик фото
    dp.include_router(journal.router)

    # 2. В конце - общий обработчик для любого другого текста и /start, /help
    dp.include_router(common.router)        # Содержит F.text, /start, /help
    # ----------------------------------------
    logging.info("Роутеры включены.")

    # --- Инициализация Базы Данных ---
    from src.services import database # Импортируем сервис БД
    database.init_db() # Создаем таблицу, если ее нет
    # --------------------------------

    # Удаляем вебхук перед запуском polling'а (важно, если бот ранее работал на вебхуках)
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Запуск polling...")
    # Запускаем бота в режиме опроса (polling)
    await dp.start_polling(bot)

def run_bot():
    """Функция для настройки логирования и запуска основной async функции."""
    # Настройка логирования с уровнем DEBUG для подробной информации
    logging.basicConfig(
        level=logging.DEBUG, # <-- Уровень DEBUG для отладки
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.info("Запуск бота Александра Элдера...")
    try:
        # Запускаем асинхронную функцию main
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Обработка штатной остановки бота (Ctrl+C)
        logger.info("Бот остановлен.")
    except Exception as e:
        # Логирование критических ошибок при запуске или работе бота
        logger.critical(f"Критическая ошибка при работе бота: {e}", exc_info=True)

# Этот блок гарантирует, что run_bot() вызывается,
# если скрипт main.py импортирует и вызывает его напрямую.
# (Хотя в нашем случае точка входа в корневом main.py)
if __name__ == '__main__':
    # Это полезно, если вы захотите запустить этот файл напрямую для тестов
    run_bot()