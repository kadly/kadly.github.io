# src/services/moex_api.py
import asyncio
import time
import logging
from typing import Dict, Any, Optional, Tuple
import aiohttp
import json
import pprint

logger = logging.getLogger(__name__)

# --- Константы ---
MOEX_ISS_URL = "https://iss.moex.com/iss"
BOARD = "TQBR"
MARKET = "shares"
ENGINE = "stock"
CACHE_TTL_SECONDS = 60

# --- Кеш и локи ---
_quote_cache: Dict[str, Tuple[float, Optional[Dict[str, Any]]]] = {}
_ticker_locks: Dict[str, asyncio.Lock] = {}

# --- Основная функция ---
async def get_moex_quote(ticker: str) -> Optional[Dict[str, Any]]:
    ticker = ticker.upper()
    current_time = time.time()

    # --- Проверка кеша ---
    if ticker in _quote_cache:
        timestamp, cached_data = _quote_cache[ticker]
        if current_time - timestamp < CACHE_TTL_SECONDS:
            logger.info(f"Кеш для {ticker}: Данные свежие, возвращаем из кеша.")
            return cached_data
        else:
             logger.info(f"Кеш для {ticker}: Данные устарели.")

    # --- Логика блокировки ---
    if ticker not in _ticker_locks:
        _ticker_locks[ticker] = asyncio.Lock()
    lock = _ticker_locks[ticker]

    async with lock:
        # Повторная проверка кеша внутри лока
        if ticker in _quote_cache:
            timestamp, cached_data = _quote_cache[ticker]
            if current_time - timestamp < CACHE_TTL_SECONDS:
                logger.info(f"Кеш для {ticker} (после лока): Данные свежие, возвращаем из кеша.")
                return cached_data

        logger.info(f"Запрос данных для {ticker} из MOEX ISS API...")
        url = (
            f"{MOEX_ISS_URL}/engines/{ENGINE}/markets/{MARKET}/boards/{BOARD}"
            f"/securities/{ticker}.json?iss.meta=off&iss.json=extended&lang=ru"
        )
        logger.debug(f"Сформированный URL: {url}")

        try:
            async with aiohttp.ClientSession() as session:
                logger.debug(f"Начало запроса GET для {ticker}")
                async with session.get(url) as response:
                    logger.debug(f"Получен ответ для {ticker}, статус: {response.status}")
                    response_text = await response.text()
                    logger.debug(f"Ответ от MOEX ISS для {ticker} (ТЕКСТ, начало):\n{response_text[:2000]}...")

                    response.raise_for_status() # Проверка статуса 4xx/5xx
                    logger.debug(f"Статус ответа {response.status} для {ticker} - OK")

                    data = None
                    try:
                         data = await response.json(content_type=None)
                         logger.info(f"JSON для {ticker} успешно распарсен.")
                         # Оставим print для контроля, если нужно
                         # print(f"\n--- RAW DATA START ({ticker}) ---")
                         # pprint.pprint(data, indent=2, width=120)
                         # print(f"--- RAW DATA END ({ticker}) ---\n")
                         logger.info(f"Полный распарсенный JSON для {ticker} (лог, начало):\n{json.dumps(data, indent=2, ensure_ascii=False, default=str)[:3000]}")
                    except Exception as json_e:
                         logger.error(f"Не удалось распарсить JSON для {ticker}: {json_e}")
                         logger.error(f"Полный текст ответа (начало): {response_text[:2000]}")
                         _quote_cache[ticker] = (current_time, None)
                         return None

                    # --- НАЧАЛО ИСПРАВЛЕННОЙ ПРОВЕРКИ ФОРМАТА ---
                    logger.debug("--- Начинаем проверку формата данных (v2) ---")
                    format_valid = True
                    error_reason = ""
                    data_block = None # Блок, где лежат securities и marketdata

                    # Шаг 1: Проверка на None/пустоту и тип list
                    if not data or not isinstance(data, list):
                        format_valid = False; error_reason = f"Данные отсутствуют или не являются списком (тип: {type(data)})."
                        logger.warning(f"Проверка формата {ticker}: {error_reason}")
                    else: logger.debug(f"Проверка формата {ticker}: Данные - список.")

                    # Шаг 2: Проверка длины списка (>= 2)
                    if format_valid and len(data) < 2:
                        format_valid = False; error_reason = f"Длина списка ({len(data)}) меньше ожидаемой (>= 2)."
                        logger.warning(f"Проверка формата {ticker}: {error_reason}")
                    elif format_valid: logger.debug(f"Проверка формата {ticker}: Длина списка ({len(data)}) достаточна.")

                    # Шаг 3: Проверка второго элемента (data[1]) на тип dict и наличие ключей
                    if format_valid:
                        if not isinstance(data[1], dict):
                            format_valid = False; error_reason = "Второй элемент (data[1]) не словарь."
                            logger.warning(f"Проверка формата {ticker}: {error_reason}")
                        elif 'securities' not in data[1]:
                            format_valid = False; error_reason = "Ключ 'securities' отсутствует в data[1]."
                            logger.warning(f"Проверка формата {ticker}: {error_reason}")
                        elif 'marketdata' not in data[1]:
                            format_valid = False; error_reason = "Ключ 'marketdata' отсутствует в data[1]."
                            logger.warning(f"Проверка формата {ticker}: {error_reason}")
                        elif not isinstance(data[1]['securities'], list) or not data[1]['securities']:
                             format_valid = False; error_reason = "Значение data[1]['securities'] не список или список пуст."
                             logger.warning(f"Проверка формата {ticker}: {error_reason}")
                        elif not isinstance(data[1]['marketdata'], list) or not data[1]['marketdata']:
                             format_valid = False; error_reason = "Значение data[1]['marketdata'] не список или список пуст."
                             logger.warning(f"Проверка формата {ticker}: {error_reason}")
                        else:
                            data_block = data[1] # Сохраняем ссылку на data[1]
                            logger.debug(f"Проверка формата {ticker}: Ключи 'securities' и 'marketdata' найдены в data[1] и их значения - непустые списки.")
                    # --- КОНЕЦ ИСПРАВЛЕННОЙ ПРОВЕРКИ ФОРМАТА ---

                    # Если формат не валиден, выходим
                    if not format_valid:
                        logger.warning(f"Неожиданный формат ответа от MOEX ISS для {ticker}. Итоговая причина: {error_reason}. Проверка не пройдена.")
                        try: logger.debug(f"Данные, не прошедшие проверку формата (начало):\n{json.dumps(data, indent=2, ensure_ascii=False, default=str)[:2000]}")
                        except Exception as dump_e: logger.error(f"Не удалось вывести данные в лог при ошибке формата: {dump_e}")
                        _quote_cache[ticker] = (current_time, None)
                        return None

                    # --- Если формат ОК, извлекаем данные ИЗ data_block (т.е. data[1]) ---
                    logger.info(f"Проверка формата для {ticker} успешно пройдена. Извлекаем данные из data[1].")
                    securities_data = data_block['securities'][0] # Берем первый элемент из списка securities
                    market_data = data_block['marketdata'][0]   # Берем первый элемент из списка marketdata

                    # --- Сборка quote_info (остается без изменений) ---
                    quote_info = {
                        "SECID": securities_data.get("SECID"),
                        "SECNAME": securities_data.get("SECNAME", "N/A"),
                        "LAST": market_data.get("LAST"),
                        "VOLTODAY": market_data.get("VOLTODAY"),
                        "VALTODAY_RUR": market_data.get("VALTODAY_RUR"),
                        "LASTTOPREVPRICE": market_data.get("LASTTOPREVPRICE"),
                        "HIGH": market_data.get("HIGH"),
                        "LOW": market_data.get("LOW"),
                        "OPEN": market_data.get("OPEN"),
                        "PREVLEGALCLOSEPRICE": securities_data.get("PREVLEGALCLOSEPRICE"),
                        "UPDATETIME": market_data.get("UPDATETIME"),
                        "SYSTIME": market_data.get("SYSTIME"),
                        "BOARDID": market_data.get("BOARDID")
                    }

                    # --- Проверка наличия ключевых данных (остается без изменений) ---
                    if quote_info["LAST"] is None and quote_info["VOLTODAY"] is None:
                         logger.warning(f"Для тикера {ticker} не найдены ключевые рыночные данные (LAST, VOLTODAY) в data[1].")
                         _quote_cache[ticker] = (current_time, None)
                         return None

                    logger.info(f"Данные для {ticker} успешно получены и обработаны.")
                    _quote_cache[ticker] = (current_time, quote_info)
                    return quote_info

        # --- Обработка исключений (остается без изменений) ---
        except aiohttp.ClientResponseError as e:
            if e.status == 404: logger.warning(f"Тикер {ticker} не найден на MOEX ISS (404).")
            else: logger.error(f"Ошибка HTTP при запросе к MOEX ISS для {ticker}: {e.status} - {e.message}", exc_info=False)
            _quote_cache[ticker] = (current_time, None); return None
        except asyncio.TimeoutError:
            logger.error(f"Таймаут при запросе к MOEX ISS для {ticker}."); return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении котировки для {ticker}: {e}", exc_info=True)
            _quote_cache[ticker] = (current_time, None); return None