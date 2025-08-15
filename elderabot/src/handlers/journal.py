# src/handlers/journal.py
import logging
import datetime
import re
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.enums import ParseMode

# Импортируем состояния и функции БД
from .journal_states import AddTradeStates
from src.services import database # Используем наш модуль БД

# Импорт утилиты форматирования (если нужна позже)
# from src.utils.message_splitter import edit_or_send_long_message

router = Router(name="journal-router")
logger = logging.getLogger(__name__)

# --- Клавиатуры ---
direction_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Long"), KeyboardButton(text="Short")]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

skip_stop_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Пропустить (без стопа)")]],
    resize_keyboard=True, one_time_keyboard=True
)

confirm_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Сохранить сделку")],
        [KeyboardButton(text="❌ Отменить ввод")]
    ],
    resize_keyboard=True, one_time_keyboard=True
)

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Отменить ввод")]],
    resize_keyboard=True, one_time_keyboard=True
)


# --- Обработчик команды /add_trade ---
@router.message(Command("add_trade"), StateFilter(None)) # Работает только если нет активного состояния
async def cmd_add_trade(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} начал добавление сделки.")
    await message.answer(
        "Хорошо, давайте добавим новую сделку. Пожалуйста, отвечайте на вопросы.\n"
        "Вы можете отменить ввод в любой момент, написав /cancel.\n\n"
        "Введите **тикер** инструмента (например, SBER, GAZP):",
        reply_markup=cancel_kb # Сразу даем кнопку отмены
    )
    await state.set_state(AddTradeStates.waiting_for_ticker)
    # Сохраняем user_id в данных состояния
    await state.update_data(user_id=message.from_user.id)


# --- Обработчик команды /cancel (в любом состоянии) ---
@router.message(Command("cancel"), StateFilter("*")) # Работает в любом состоянии
@router.message(F.text.casefold() == "❌ отменить ввод", StateFilter("*"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активной операции для отмены.", reply_markup=ReplyKeyboardRemove())
        return

    logger.info(f"Пользователь {message.from_user.id} отменил операцию из состояния {current_state}.")
    await state.clear()
    await message.answer("Ввод отменен.", reply_markup=ReplyKeyboardRemove())


# --- Обработчики состояний FSM ---

# 1. Получение тикера
@router.message(AddTradeStates.waiting_for_ticker, F.text)
async def process_ticker(message: Message, state: FSMContext):
    ticker = message.text.strip().upper()
    # TODO: Добавить валидацию тикера (например, запрос к MOEX API или проверка по списку)
    if not re.match(r"^[A-Z]{1,10}$", ticker): # Простая проверка на буквы и длину
         await message.reply("Некорректный формат тикера. Пожалуйста, введите тикер (только латинские буквы, например, SBER):", reply_markup=cancel_kb)
         return

    await state.update_data(ticker=ticker)
    await message.answer(f"Тикер: {ticker}. Теперь введите **цену входа** (число, разделитель - точка):", reply_markup=cancel_kb)
    await state.set_state(AddTradeStates.waiting_for_entry_price)

# 2. Получение цены входа
@router.message(AddTradeStates.waiting_for_entry_price, F.text)
async def process_entry_price(message: Message, state: FSMContext):
    try:
        price = float(message.text.strip().replace(',', '.')) # Заменяем запятую на точку
        if price <= 0: raise ValueError("Цена должна быть положительной")
        await state.update_data(entry_price=price)
        await message.answer(f"Цена входа: {price}. Теперь введите **размер позиции** (в лотах или штуках, число):", reply_markup=cancel_kb)
        await state.set_state(AddTradeStates.waiting_for_position_size)
    except ValueError:
        await message.reply("Некорректный формат цены. Введите число (разделитель - точка), например, 150.75:", reply_markup=cancel_kb)

# 3. Получение размера позиции
@router.message(AddTradeStates.waiting_for_position_size, F.text)
async def process_position_size(message: Message, state: FSMContext):
    try:
        size = float(message.text.strip().replace(',', '.'))
        if size <= 0: raise ValueError("Размер позиции должен быть положительным")
        await state.update_data(position_size=size)
        await message.answer(f"Размер позиции: {size}. Выберите **направление** сделки:", reply_markup=direction_kb) # Клавиатура Long/Short
        await state.set_state(AddTradeStates.waiting_for_direction)
    except ValueError:
        await message.reply("Некорректный формат размера. Введите число, например, 10:", reply_markup=cancel_kb)

# 4. Получение направления
@router.message(AddTradeStates.waiting_for_direction, F.text.casefold().in_({"long", "short"}))
async def process_direction(message: Message, state: FSMContext):
    direction = message.text.strip().lower()
    await state.update_data(direction=direction)
    await message.answer(
        f"Направление: {direction.capitalize()}. Теперь введите **цену стоп-лосса** (число) или нажмите 'Пропустить'.",
        reply_markup=skip_stop_kb # Клавиатура с кнопкой пропуска
    )
    await state.set_state(AddTradeStates.waiting_for_stop_loss)

@router.message(AddTradeStates.waiting_for_direction) # Если ввели не Long/Short
async def process_direction_invalid(message: Message):
    await message.reply("Пожалуйста, выберите направление с помощью кнопок: Long или Short.", reply_markup=direction_kb)


# 5. Получение стоп-лосса (или пропуск)
@router.message(AddTradeStates.waiting_for_stop_loss, F.text)
async def process_stop_loss(message: Message, state: FSMContext):
    stop_loss_price = None
    if message.text.strip().lower() == "пропустить (без стопа)":
        logger.info(f"Пользователь {message.from_user.id} пропустил ввод стоп-лосса.")
        await state.update_data(stop_loss_price=None)
    else:
        try:
            price = float(message.text.strip().replace(',', '.'))
            if price <= 0: raise ValueError("Цена стопа должна быть положительной")
            stop_loss_price = price
            await state.update_data(stop_loss_price=price)
        except ValueError:
            await message.reply("Некорректный формат цены стоп-лосса. Введите число (разделитель - точка) или нажмите 'Пропустить'.", reply_markup=skip_stop_kb)
            return # Остаемся в том же состоянии

    sl_info = f"Стоп-лосс: {stop_loss_price}" if stop_loss_price else "Стоп-лосс: Не установлен"
    await message.answer(
        f"{sl_info}. Теперь опишите **причину входа** (сигнал, идея, паттерн):",
        reply_markup=cancel_kb # Убираем кнопки про стоп
    )
    await state.set_state(AddTradeStates.waiting_for_entry_reason)


# 6. Получение причины входа
@router.message(AddTradeStates.waiting_for_entry_reason, F.text)
async def process_entry_reason(message: Message, state: FSMContext):
    reason = message.text.strip()
    if not reason:
        await message.reply("Причина входа не может быть пустой. Опишите вашу идею.", reply_markup=cancel_kb)
        return
    if len(reason) > 500: # Ограничим длину
         await message.reply("Слишком длинное описание причины (макс. 500 символов). Попробуйте короче.", reply_markup=cancel_kb)
         return

    await state.update_data(entry_reason=reason)

    # --- Собираем все данные для показа пользователю ---
    trade_draft = await state.get_data()
    # Добавляем текущую дату и время как дату входа по умолчанию
    entry_dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await state.update_data(entry_date=entry_dt) # Сохраняем и в состояние
    trade_draft['entry_date'] = entry_dt # Для показа

    summary_lines = [
        "**Проверьте данные сделки:**",
        f"- Тикер: {trade_draft.get('ticker')}",
        f"- Дата входа: {trade_draft.get('entry_date')}",
        f"- Цена входа: {trade_draft.get('entry_price')}",
        f"- Размер позиции: {trade_draft.get('position_size')}",
        f"- Направление: {trade_draft.get('direction', '').capitalize()}",
        f"- Стоп-лосс: {trade_draft.get('stop_loss_price', 'Не установлен')}",
        f"- Причина входа: {trade_draft.get('entry_reason')}"
    ]
    summary_text = "\n".join(summary_lines)

    await message.answer(summary_text, reply_markup=confirm_kb, parse_mode=ParseMode.MARKDOWN)
    await state.set_state(AddTradeStates.confirm_trade)


# 7. Подтверждение и сохранение
@router.message(AddTradeStates.confirm_trade, F.text.casefold() == "✅ сохранить сделку")
async def process_confirm_trade(message: Message, state: FSMContext):
    trade_data = await state.get_data()
    logger.info(f"Пользователь {message.from_user.id} подтвердил сделку: {trade_data}")

    # Вызываем функцию добавления в БД
    trade_id = database.add_trade(trade_data)

    if trade_id:
        await message.answer(f"✅ Сделка успешно добавлена в журнал! ID сделки: {trade_id}", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("❌ Произошла ошибка при сохранении сделки в базу данных. Попробуйте позже.", reply_markup=ReplyKeyboardRemove())

    await state.clear() # Завершаем FSM

@router.message(AddTradeStates.confirm_trade) # Если нажали не ту кнопку
async def process_confirm_invalid(message: Message):
     await message.reply("Пожалуйста, используйте кнопки для подтверждения или отмены.", reply_markup=confirm_kb)


# --- Обработчик команды /my_trades ---
@router.message(Command("my_trades"), StateFilter(None))
async def cmd_my_trades(message: Message):
    user_id = message.from_user.id
    trades = database.get_user_trades(user_id, limit=5) # Получаем последние 5

    if not trades:
        await message.answer("У вас пока нет записей в торговом журнале. Используйте /add_trade для добавления.")
        return

    response_text = "**Ваши последние сделки:**\n\n"
    for trade in trades:
        trade_id = trade.get('trade_id')
        ticker = trade.get('ticker')
        entry_date = trade.get('entry_date', '').split(' ')[0] # Только дата
        direction = trade.get('direction', '').capitalize()
        entry_price = trade.get('entry_price')
        exit_price = trade.get('exit_price') # Будет None для открытых
        status = "Закрыта" if exit_price is not None else "Открыта"
        # TODO: Добавить расчет PnL если закрыта

        response_text += f"ID: {trade_id} | {entry_date} | {ticker} {direction} @ {entry_price} | Статус: {status}\n"
        # Можно добавить больше деталей или кнопку для просмотра/анализа

    await message.answer(response_text, parse_mode=ParseMode.MARKDOWN)


# TODO: Добавить команду /analyze_last_trade или /analyze_trade <id>