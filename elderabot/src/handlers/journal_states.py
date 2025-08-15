# src/handlers/journal_states.py
from aiogram.fsm.state import State, StatesGroup

class AddTradeStates(StatesGroup):
    waiting_for_ticker = State()
    waiting_for_entry_price = State()
    waiting_for_position_size = State()
    waiting_for_direction = State()
    waiting_for_stop_loss = State() # Сделаем ввод стопа отдельным шагом
    waiting_for_entry_reason = State()
    confirm_trade = State() # Опциональное состояние для подтверждения