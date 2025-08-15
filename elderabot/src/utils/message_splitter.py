# src/utils/message_splitter.py (Новый файл)
import logging
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)

TELEGRAM_MAX_MESSAGE_LENGTH = 4096

async def edit_or_send_long_message(
    target_message: Message, # Сообщение, которое нужно отредактировать или после которого отправить
    text: str,
    parse_mode: ParseMode | None = None # Передаем нужный parse_mode
):
    """
    Редактирует существующее сообщение или отправляет новое(ые),
    разбивая длинный текст на части.
    Первую часть пытается вставить через edit_text, остальные - через send_message.
    """
    if not text:
        logger.warning("Попытка отправить пустой текст.")
        try:
            # Отредактируем на какое-то сообщение по умолчанию
            await target_message.edit_text("Получен пустой ответ от ИИ.", parse_mode=None)
        except Exception:
             pass # Игнорируем ошибки редактирования здесь
        return

    # Разбиваем текст на части по лимиту Telegram
    # Стараемся разбивать по переносу строки для читаемости
    parts = []
    current_part = ""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # Проверяем, не превысит ли добавление новой строки лимит
        if len(current_part) + len(line) + 1 > TELEGRAM_MAX_MESSAGE_LENGTH:
            # Если текущая часть не пуста, добавляем ее
            if current_part:
                parts.append(current_part)
            # Если одна строка сама по себе длиннее лимита, режем ее грубо
            if len(line) > TELEGRAM_MAX_MESSAGE_LENGTH:
                for k in range(0, len(line), TELEGRAM_MAX_MESSAGE_LENGTH):
                     parts.append(line[k:k + TELEGRAM_MAX_MESSAGE_LENGTH])
                current_part = "" # Начинаем новую часть после разрезанной строки
            else:
                current_part = line # Начинаем новую часть с этой строки
        else:
            # Добавляем строку к текущей части
            if current_part:
                current_part += "\n" + line
            else:
                current_part = line

        # Добавляем последнюю строку, если она не пустая и мы на последней итерации
        if i == len(lines) - 1 and current_part:
             parts.append(current_part)

    # Если разбивка не дала частей (например, текст был очень коротким)
    if not parts and text:
         parts.append(text)

    logger.info(f"Сообщение разбито на {len(parts)} частей.")

    # Отправляем/редактируем части
    message_to_edit = target_message # Первое сообщение редактируем
    is_first_part = True

    for i, part in enumerate(parts):
        logger.debug(f"Отправка/редактирование части {i+1}/{len(parts)}, длина: {len(part)}")
        try:
            if is_first_part:
                await message_to_edit.edit_text(part, parse_mode=parse_mode)
                is_first_part = False
            else:
                # Последующие части отправляем как новые сообщения
                # Отправляем в тот же чат и отвечаем на исходное сообщение пользователя
                # или на предыдущее сообщение бота для связности (но это сложнее)
                await target_message.reply(part, parse_mode=parse_mode)
                # Небольшая пауза между сообщениями, чтобы избежать флуда
                # import asyncio
                # await asyncio.sleep(0.5)
        except TelegramBadRequest as e:
            logger.error(f"Ошибка Telegram при отправке/редактировании части {i+1}: {e}")
            # Если даже часть не уходит, можно попробовать без parse_mode
            if parse_mode is not None:
                 logger.warning(f"Повторная попытка отправки части {i+1} без parse_mode.")
                 try:
                     if is_first_part:
                          await message_to_edit.edit_text(part, parse_mode=None)
                          is_first_part = False
                     else:
                          await target_message.reply(part, parse_mode=None)
                 except Exception as e_fallback:
                      logger.error(f"Ошибка при повторной отправке части {i+1} без parse_mode: {e_fallback}")
                      # Если и так не ушло, пропускаем часть или сообщаем об ошибке
                      if is_first_part: # Если первая часть не ушла, сообщаем об ошибке
                          try: await message_to_edit.edit_text(f"❌ Ошибка отображения части {i+1} ответа.", parse_mode=None)
                          except: pass
                          is_first_part = False # Чтобы не пытаться редактировать снова
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке/редактировании части {i+1}: {e}", exc_info=True)
            if is_first_part:
                try: await message_to_edit.edit_text(f"❌ Ошибка отображения части {i+1} ответа.", parse_mode=None)
                except: pass
                is_first_part = False