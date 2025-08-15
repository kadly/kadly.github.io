# src/services/database.py
import sqlite3
import logging
import datetime
import os
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# DB_FILE = "trading_journal.db" # Файл базы данных будет в корне проекта
DB_DIR = "/data" # Директория внутри контейнера для volume
DB_FILE = os.path.join(DB_DIR, "trading_journal.db") # Полный путь

def init_db():
    """Инициализирует базу данных и создает таблицу trades, если она не существует."""
    conn = None
    try:
        # --- ДОБАВЛЕНО: Создаем директорию /data, если ее нет ---
        if not os.path.exists(DB_DIR):
            logger.info(f"Создание директории для БД: {DB_DIR}")
            os.makedirs(DB_DIR)
            # Можно добавить установку прав, если нужно, но обычно Docker Volumes сами справляются
            # os.chmod(DB_DIR, 0o777) # Пример (не рекомендуется без необходимости)
        # --------------------------------------------------

        logger.info(f"Попытка подключения к БД: {DB_FILE}")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        logger.debug("Соединение установлено, создаем таблицу (если нет)...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                entry_date TEXT NOT NULL,
                entry_price REAL NOT NULL,
                position_size REAL NOT NULL,
                direction TEXT NOT NULL CHECK(direction IN ('long', 'short')),
                stop_loss_price REAL,
                entry_reason TEXT NOT NULL,
                exit_date TEXT,
                exit_price REAL,
                exit_reason TEXT,
                pnl REAL,
                notes TEXT,
                added_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        logger.info(f"База данных '{DB_FILE}' инициализирована, таблица 'trades' готова.")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при инициализации базы данных SQLite '{DB_FILE}': {e}", exc_info=True)
        if "unable to open" in str(e) or "read-only" in str(e):
             logger.error("-> Проверьте права доступа к директории монтирования volume внутри контейнера или настройки volume.")
    except Exception as e:
        logger.error(f"Неожиданная ошибка при инициализации БД: {e}", exc_info=True)
    finally:
        if conn:
            try:
                conn.close()
                logger.debug("Соединение с БД закрыто.")
            except sqlite3.Error as e:
                logger.error(f"Ошибка при закрытии соединения с БД: {e}")

def add_trade(trade_data: Dict[str, Any]) -> Optional[int]:
    """
    Добавляет новую сделку в базу данных.

    Args:
        trade_data: Словарь с данными сделки. Должен содержать ключи:
                    user_id, ticker, entry_date, entry_price, position_size,
                    direction, entry_reason, stop_loss_price (может быть None).

    Returns:
        ID добавленной сделки или None в случае ошибки.
    """
    required_keys = {"user_id", "ticker", "entry_date", "entry_price", "position_size", "direction", "entry_reason"}
    if not required_keys.issubset(trade_data.keys()):
        logger.error(f"Недостаточно данных для добавления сделки: {trade_data}")
        return None

    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO trades (user_id, ticker, entry_date, entry_price, position_size, direction, entry_reason, stop_loss_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trade_data["user_id"],
            trade_data["ticker"].upper(), # Сохраняем тикер в верхнем регистре
            trade_data["entry_date"],
            trade_data["entry_price"],
            trade_data["position_size"],
            trade_data["direction"].lower(), # long или short
            trade_data["entry_reason"],
            trade_data.get("stop_loss_price") # Используем get, т.к. может быть None
        ))
        trade_id = cursor.lastrowid # Получаем ID вставленной записи
        conn.commit()
        logger.info(f"Сделка user_id={trade_data['user_id']} ticker={trade_data['ticker']} успешно добавлена с ID={trade_id}.")
        return trade_id
    except sqlite3.Error as e:
        logger.error(f"Ошибка SQLite при добавлении сделки для user_id={trade_data.get('user_id')}: {e}", exc_info=True)
        if conn:
            conn.rollback() # Откатываем изменения при ошибке
        return None
    finally:
        if conn:
            conn.close()

def get_user_trades(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Получает последние N сделок пользователя."""
    conn = None
    trades = []
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row # Возвращать результаты как словари
        cursor = conn.cursor()
        cursor.execute("""
            SELECT trade_id, ticker, entry_date, entry_price, position_size, direction, stop_loss_price, entry_reason, exit_date, exit_price, exit_reason, pnl, notes
            FROM trades
            WHERE user_id = ?
            ORDER BY added_timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        trades = [dict(row) for row in cursor.fetchall()]
        logger.info(f"Найдено {len(trades)} сделок для user_id={user_id} (лимит {limit}).")
    except sqlite3.Error as e:
        logger.error(f"Ошибка SQLite при получении сделок user_id={user_id}: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()
    return trades

# Добавьте здесь другие функции по мере необходимости (get_trade_by_id, update_trade и т.д.)