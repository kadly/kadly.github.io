import io
import logging

from aiogram import Router, F, Bot
from aiogram.types import Message, ContentType
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError, TelegramForbiddenError

from src.services.gemini import get_elder_image_analysis
from src.utils.message_splitter import edit_or_send_long_message

router = Router(name="image-analysis-router")
logger = logging.getLogger(__name__)

# Максимальный размер файла для скачивания (в байтах), например, 15 МБ
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024

@router.message(F.content_type == ContentType.PHOTO)
async def handle_photo_analysis(message: Message, bot: Bot):
    """
    Обрабатывает получение фотографии для анализа.
    """
    # ---- Начало функции ---- (Уровень 0 отступа)

    if not message.photo:
        logger.warning("Сообщение с ContentType.PHOTO не содержит message.photo")
        return # Ничего не делаем, если нет фото

    # Выбираем фото наибольшего разрешения
    photo = message.photo[-1] # Уровень 1 отступа

    # Проверка размера файла
    if photo.file_size is not None and photo.file_size > MAX_FILE_SIZE_BYTES:
        await message.answer("🚫 Файл слишком большой. Пожалуйста, отправьте изображение размером менее 15 МБ.")
        return

    status_message = None # Инициализируем переменную для сообщения статуса
    try:
        status_message = await message.reply("⏳ Получил ваш график. Отправляю доктору Элдеру на анализ... Это может занять некоторое время.")
    except TelegramForbiddenError:
        logger.warning(f"Не могу ответить пользователю {message.from_user.id} - возможно, бот заблокирован.")
        return # Не можем отправить статус, нет смысла продолжать
    except Exception as e:
        logger.error(f"Не удалось отправить статусное сообщение пользователю {message.from_user.id}: {e}")
        return # Если даже статус не ушел, дальше сложно

    # Скачивание файла
    image_bytes = None
    image_bytes_io = io.BytesIO()
    try:
        downloaded_file = await bot.get_file(photo.file_id)
        if downloaded_file.file_size is not None and downloaded_file.file_size > MAX_FILE_SIZE_BYTES:
             # Доп. проверка размера после получения информации о файле
             await status_message.edit_text("🚫 Файл слишком большой после проверки. Пожалуйста, отправьте изображение размером менее 15 МБ.")
             return

        logger.info(f"Скачивание файла {downloaded_file.file_path}...")
        await bot.download_file(downloaded_file.file_path, destination=image_bytes_io)
        image_bytes = image_bytes_io.getvalue()
        logger.info(f"Файл скачан, размер: {len(image_bytes) / 1024:.1f} KB")

    except TelegramNetworkError as e:
        logger.error(f"Сетевая ошибка Telegram при скачивании файла {photo.file_id}: {e}")
        await status_message.edit_text("🚫 Проблема с сетью при скачивании файла из Telegram. Попробуйте еще раз позже.")
        return
    except TelegramBadRequest as e:
        logger.error(f"Ошибка Telegram API (Bad Request) при скачивании файла {photo.file_id}: {e}")
        await status_message.edit_text("🚫 Не удалось скачать файл изображения из Telegram (возможно, неверный ID). Попробуйте еще раз или используйте другое изображение.")
        return
    except Exception as e: # Ловим другие возможные ошибки download
        logger.error(f"Неожиданная ошибка при скачивании файла {photo.file_id}: {e}", exc_info=True)
        await status_message.edit_text("🚫 Произошла ошибка при обработке файла перед отправкой на анализ. Попробуйте еще раз.")
        return
    finally:
        image_bytes_io.close() # Всегда закрываем поток

    if not image_bytes:
        logger.warning("Скачанный файл оказался пустым или не был получен.")
        await status_message.edit_text("🚫 Скачанный файл оказался пустым. Попробуйте еще раз.")
        return

    user_caption = message.caption # Текст подписи к фото

    logger.info(f"Запрос на анализ графика от user_id={message.from_user.id}. Caption: '{user_caption}'")

    # ---- Основной блок анализа и отправки ответа ----
    try: # <--- НАЧАЛО ВНЕШНЕГО TRY (Уровень 1 отступа)
        # Вызываем функцию анализа из сервиса Gemini
        analysis_result = await get_elder_image_analysis(user_caption, image_bytes) # Уровень 2
        
        await edit_or_send_long_message(
            target_message=status_message,
            text=analysis_result,
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e: # <--- ВНЕШНИЙ EXCEPT (Уровень 1 отступа). ВОТ ЗДЕСЬ БЫЛА ОШИБКА. Должен быть на одном уровне с внешним try.
        # Ловим ошибки, которые могли произойти в get_elder_image_analysis
        logger.error(f"Критическая ошибка во время анализа изображения или отправки: {e}", exc_info=True) # Уровень 2
        try:
            await status_message.edit_text("❌ Произошла серьезная ошибка во время анализа. Команда разработчиков уже уведомлена (надеюсь). Попробуйте позже.", parse_mode=None) # Уровень 3
        except Exception as final_e:
             logger.error(f"Не удалось даже отправить сообщение об ошибке анализа пользователю: {final_e}") # Уровень 3

# ---- Конец функции ----