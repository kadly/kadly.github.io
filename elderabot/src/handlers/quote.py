import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandObject # Используем CommandObject
from aiogram.types import Message
from aiogram.enums import ParseMode

from src.services.moex_api import get_moex_quote # Импортируем нашу функцию

router = Router(name="quote-router")
logger = logging.getLogger(__name__)

@router.message(Command(commands=['quote'], ignore_mention=True))
async def handle_quote_command(message: Message, command: CommandObject):
    """
    Обрабатывает команду /quote <ТИКЕР> для получения котировки с MOEX.
    """
    if command.args is None:
        await message.reply(
            "Пожалуйста, укажите тикер акции после команды.\n"
            "Пример: `/quote SBER`",
            parse_mode=ParseMode.MARKDOWN # Используем Markdown для примера
        )
        return

    ticker = command.args.strip().upper()
    logger.info(f"Запрос котировки для тикера: {ticker} от user_id={message.from_user.id}")

    status_msg = await message.reply(f"⏳ Запрашиваю котировку для {ticker}...")

    quote_data = await get_moex_quote(ticker)

    if quote_data:
        # Форматируем ответ
        try:
            change_percent = quote_data.get('LASTTOPREVPRICE')
            change_sign = "+" if change_percent is not None and change_percent > 0 else ""
            change_str = f"{change_sign}{change_percent:.2f}%" if change_percent is not None else "N/A"

            vol_today = quote_data.get('VOLTODAY')
            vol_str = f"{vol_today:,}".replace(',', ' ') if vol_today is not None else "N/A" # Форматируем объем

            response_lines = [
                f"*{quote_data.get('SECNAME', ticker)}* ({quote_data.get('SECID')}) - MOEX {quote_data.get('BOARDID', 'TQBR')}",
                f"Цена: *{quote_data.get('LAST', 'N/A')}* RUB ({change_str})",
                f"Объем (шт.): {vol_str}",
                f"Дневной диапазон: {quote_data.get('LOW', 'N/A')} - {quote_data.get('HIGH', 'N/A')}",
                f"Открытие: {quote_data.get('OPEN', 'N/A')}",
                f"Закрытие пред.: {quote_data.get('PREVLEGALCLOSEPRICE', 'N/A')}",
                f"Время обновления: {quote_data.get('UPDATETIME', 'N/A')} ({quote_data.get('SYSTIME', 'N/A')})"
            ]
            response_text = "\n".join(response_lines)
            await status_msg.edit_text(response_text, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
             logger.error(f"Ошибка форматирования или отправки ответа для {ticker}: {e}", exc_info=True)
             await status_msg.edit_text(f"Не удалось обработать данные для {ticker}. Попробуйте позже.")

    else:
        await status_msg.edit_text(f"Не удалось получить данные для тикера *{ticker}*. Убедитесь, что тикер правильный и торгуется на MOEX (TQBR).", parse_mode=ParseMode.MARKDOWN)