# src/services/gemini.py

import google.generativeai as genai
import PIL.Image
import io
import logging
import time
import chromadb
import re # <-- Для регулярных выражений
from typing import List, Optional, Dict, Any # <-- Для типизации

# --- Импортируем сервисы ---
from .moex_api import get_moex_quote # Импортируем функцию котировок

from src.config import (
    GEMINI_API_KEY,
    ELDER_VISION_PROMPT,
    ELDER_TEXT_PROMPT, # Убедитесь, что этот промпт обновлен согласно предыдущему ответу
    CHROMA_DATA_PATH,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    RAG_TOP_K, 
    DISTANCE_THRESHOLD
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
# Можно установить уровень DEBUG для более детального логирования
# logging.getLogger().setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# --- Инициализация Gemini API ---
vision_model = None
text_model = None
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # Модель для Vision
    vision_model = genai.GenerativeModel('gemini-1.5-flash-latest')
    # Модель для Текста
    text_model = genai.GenerativeModel('gemini-1.5-flash-latest')
    # Модель для Эмбеддингов будет использоваться через genai.embed_content
    logger.info("Модели Gemini (Vision, Text, Embedding) инициализированы.")
except Exception as e:
    logger.critical(f"Критическая ошибка инициализации Gemini: {e}", exc_info=True)
    # Оставляем модели None при ошибке

# --- Инициализация ChromaDB Клиента ---
chroma_client = None
chroma_collection = None # Инициализируем как None
try:
    chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    logger.info(f"ChromaDB клиент подключен к данным в: {CHROMA_DATA_PATH}")

    # --- Получение коллекции (адаптировано под разные версии ChromaDB) ---
    try:
        collection_maybe = chroma_client.get_collection(name=COLLECTION_NAME)
        chroma_collection = collection_maybe
        logger.info(f"ChromaDB коллекция '{COLLECTION_NAME}' успешно получена.")
        if not chroma_collection:
           logger.error(f"Метод get_collection для '{COLLECTION_NAME}' вернул None, коллекция не доступна.")

    except Exception as e_coll: # Ловим ЛЮБОЕ исключение при получении
        error_message = str(e_coll).lower()
        not_found_markers = ["not found", "does not exist", "no collection", f"collection '{COLLECTION_NAME.lower()}'"]
        if "collection" in error_message and any(marker in error_message for marker in not_found_markers):
             logger.error(f"Коллекция '{COLLECTION_NAME}' не найдена в ChromaDB по пути '{CHROMA_DATA_PATH}'. Запустите скрипт preprocess_books.py!")
        else:
             logger.error(f"Неожиданная ошибка при получении коллекции '{COLLECTION_NAME}': {e_coll}", exc_info=True)
        # chroma_collection остается None

except Exception as e:
    logger.critical(f"Критическая ошибка инициализации ChromaDB клиента: {e}", exc_info=True)
    # chroma_client и chroma_collection останутся None

# --- Утилита распознавания тикеров ---
KNOWN_TICKERS = {"SBER", "GAZP", "LKOH", "ROSN", "GMKN", "NVTK", "PLZL", "SNGS", "TATN", "YNDX", "VTBR", "ALRS", "CHMF", "MGNT", "NLMK", "POLY", "SBERP", "SNGSP", "TRNFP", "MOEX", "MTSS", "VKCO", "OZON", "POSI", "FIVE", "IRAO", "PIKK", "T", "AFKS", "MAGN", "RTKM", "HYDR", "FEES", "UPRO"} # Дополненный список
TICKER_REGEX = re.compile(r'\b([A-Z]{4,5})\b') # 4-5 заглавных латинских букв

def find_tickers_in_text(text: str) -> List[str]:
    """Находит потенциальные тикеры MOEX в тексте."""
    if not text:
        return []

    potential_tickers_re = TICKER_REGEX.findall(text.upper())
    found_tickers = set(potential_tickers_re)

    # Ищем по списку известных тикеров (может найти и те, что не совпали с регуляркой)
    words = re.findall(r'\b[A-Z]+\b', text.upper())
    for word in words:
        if word in KNOWN_TICKERS:
            found_tickers.add(word)

    logger.debug(f"Найденные потенциальные тикеры: {list(found_tickers)}")
    # Возвращаем только те, что есть в нашем списке (для большей надежности)
    # Либо можно возвращать все найденные `list(found_tickers)`
    reliable_tickers = [t for t in found_tickers if t in KNOWN_TICKERS]
    logger.debug(f"Надежные тикеры (известные): {reliable_tickers}")
    return reliable_tickers

# --- Функция поиска релевантных чанков (ОБНОВЛЕННАЯ с фильтрацией) ---
async def find_relevant_chunks(user_query: str, n_results: int = RAG_TOP_K) -> list[str]:
    """
    Ищет релевантные чанки в ChromaDB, фильтруя их по порогу расстояния.
    """
    if not chroma_collection:
        logger.warning("Поиск по ChromaDB невозможен: коллекция не инициализирована.")
        return []
    if not user_query:
        logger.warning("Получен пустой запрос для поиска чанков.")
        return []

    try:
        # 1. Вычисление эмбеддинга запроса (без изменений)
        logger.debug(f"Вычисление эмбеддинга для запроса: '{user_query[:100]}...'")
        query_embedding_result = await genai.embed_content_async(
            model=EMBEDDING_MODEL_NAME,
            content=user_query,
            task_type="RETRIEVAL_QUERY"
        )
        if 'embedding' not in query_embedding_result or not query_embedding_result['embedding']:
             logger.error("Не удалось получить эмбеддинг для запроса пользователя.")
             return []
        query_vector = query_embedding_result['embedding']
        logger.debug(f"Эмбеддинг для запроса получен.")

        # 2. Выполнение поиска в ChromaDB (запрашиваем n_results)
        logger.info(f"Поиск топ-{n_results} кандидатов в ChromaDB для запроса: '{user_query[:50]}...'")
        results = chroma_collection.query(
            query_embeddings=[query_vector],
            n_results=n_results, # Запрашиваем K кандидатов
            include=['documents', 'metadatas', 'distances'] # Важно запросить distances!
        )

        # 3. Фильтрация результатов по DISTANCE_THRESHOLD
        filtered_docs = []
        log_details = []

        if results and results.get('documents') and results['documents'][0]:
            documents = results['documents'][0]
            distances = results.get('distances', [[None]*len(documents)])[0]
            metadatas = results.get('metadatas', [[{}]*len(documents)])[0]

            logger.debug(f"Получено {len(documents)} кандидатов от ChromaDB. Фильтруем по порогу < {DISTANCE_THRESHOLD}...")

            for i, doc in enumerate(documents):
                dist = distances[i]
                source = metadatas[i].get('source', 'N/A')
                log_entry = f"'{source}' (dist: {dist:.4f})"

                if dist is not None and dist < DISTANCE_THRESHOLD: # <-- Основное условие фильтрации
                    filtered_docs.append(doc)
                    log_details.append(log_entry + " - OK")
                    logger.debug(f"  Чанк {i+1} прошел фильтр: {log_entry}")
                else:
                    # Логируем, почему чанк был отброшен
                    reason = "N/A" if dist is None else f">= {DISTANCE_THRESHOLD}"
                    logger.debug(f"  Чанк {i+1} отброшен: {log_entry} (причина: расстояние {reason})")

            if filtered_docs:
                 logger.info(f"Найдено {len(filtered_docs)} релевантных чанков (после фильтрации): {', '.join(log_details)}")
            else:
                 logger.info(f"Релевантные чанки, прошедшие фильтр (< {DISTANCE_THRESHOLD}), не найдены.")

            return filtered_docs # Возвращаем отфильтрованный список документов
        else:
            logger.info(f"Кандидаты в ChromaDB не найдены для запроса: '{user_query[:50]}...'")
            return []

    except Exception as e:
        logger.error(f"Ошибка во время поиска/фильтрации в ChromaDB для запроса '{user_query[:50]}...': {e}", exc_info=True)
        return []

# --- Функция анализа изображений (остается без изменений) ---
async def get_elder_image_analysis(user_prompt: str | None, image_bytes: bytes) -> str:
    """
    Анализирует изображение графика с помощью Gemini Vision API в роли Элдера.
    """
    if not vision_model:
         return "Ошибка: Модель Gemini Vision не была инициализирована. Проверьте API ключ и конфигурацию."
    try:
        img = PIL.Image.open(io.BytesIO(image_bytes))
        final_prompt_parts = [ELDER_VISION_PROMPT]
        if user_prompt:
            final_prompt_parts.append(f"\nUser's comment on the chart:\n'{user_prompt}'\n\nAnalyze the chart:")
        else:
            final_prompt_parts.append("\nAnalyze this chart:")
        final_prompt_parts.append(img)

        logger.info("Отправка запроса к Gemini Vision API...")
        response = await vision_model.generate_content_async(final_prompt_parts, stream=False)

        # Обработка ответа
        if response.parts:
             analysis_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
             logger.info("Ответ от Gemini Vision API получен.")
             return analysis_text.strip()
        elif response.prompt_feedback and response.prompt_feedback.block_reason:
             reason = response.prompt_feedback.block_reason.name
             logger.warning(f"Ответ Gemini Vision заблокирован. Причина: {reason}")
             if reason == "SAFETY": return "Sorry, I cannot process this image due to content safety restrictions. Please try another chart."
             else: return f"Could not get response from the vision model. Block reason: {reason}."
        elif hasattr(response, 'text') and response.text:
             logger.warning(f"Gemini Vision returned general text, possibly an error: {response.text}")
             if "no content" in response.text.lower(): return "Sorry, the model could not generate a response for this image. Please try again."
             else: return f"Could not get a detailed analysis: {response.text}"
        else:
             logger.error(f"Could not extract text from Gemini Vision response. Response: {response}")
             return "Sorry, I could not get a structured response from the vision model. Please try again later."
    except Exception as e:
        logger.error(f"Ошибка при взаимодействии с Gemini Vision API: {e}", exc_info=True)
        return f"An internal error occurred during image analysis ({type(e).__name__}). Please try again later."

# --- Функция генерации текстового ответа (V4 - с поиском тикера в истории) ---
async def get_elder_text_response(user_message: str, chat_history: List[Dict[str, Any]] = None) -> str:
    """
    Генерирует текстовый ответ в стиле Элдера, используя RAG, котировки, историю диалога,
    и пытается определить контекстный тикер из истории для уточняющих вопросов.
    """
    if not text_model:
        return "Ошибка: Текстовая модель Gemini не была инициализирована."
    if not user_message:
        return "Пожалуйста, задайте вопрос."
    if chat_history is None:
        chat_history = []

    logger.info(f"Начинаем RAG+Quote+History v4 процесс для: '{user_message[:100]}...'")

    # --- Шаг 1: Поиск релевантных чанков (RAG) ---
    relevant_chunks = await find_relevant_chunks(user_message)
    context_from_books_str = ""
    if relevant_chunks:
        context_from_books_str = "\n\n--- Relevant Excerpts from My Books ---\n"
        for i, chunk in enumerate(relevant_chunks):
            context_from_books_str += f"\n[Excerpt {i+1}]:\n{chunk.strip()}\n"
        context_from_books_str += "\n--- End of Excerpts ---\n"
        logger.info(f"Добавлено {len(relevant_chunks)} RAG чанков в контекст.")
    else:
        context_from_books_str = "\n(Note: I searched my writings but didn't find a highly relevant excerpt...)\n"
        logger.info("Релевантные чанки не найдены.")


    # --- Шаг 2: Определение Контекстного Тикера и Получение Котировки ---
    ticker_context: Optional[str] = None
    quote_data_to_use: Optional[Dict[str, Any]] = None # Данные котировки для добавления в промпт

    current_tickers = find_tickers_in_text(user_message)

    if current_tickers:
        # Если тикер есть в текущем сообщении, берем первый надежный
        ticker_context = current_tickers[0]
        logger.info(f"Тикер '{ticker_context}' найден в текущем сообщении.")
    else:
        # Ищем тикер в недавней истории (последние 4 сообщения / 2 пары)
        if chat_history:
            logger.debug("Тикер в текущем сообщении не найден, ищем в истории...")
            ticker_from_history = None
            for msg in reversed(chat_history[-4:]): # Смотрим последние 4 сообщения
                role = msg.get('role')
                text_parts = msg.get('parts')
                if text_parts and isinstance(text_parts, list) and text_parts[0]:
                    text = text_parts[0]
                    # Ищем тикеры и в сообщениях пользователя, и в ответах бота (т.к. бот мог их упомянуть)
                    found_in_hist = find_tickers_in_text(text)
                    if found_in_hist:
                        ticker_from_history = found_in_hist[0] # Берем первый найденный в истории
                        logger.info(f"Тикер '{ticker_from_history}' найден в недавней истории (роль: {role}).")
                        break # Нашли самый недавний, выходим

            if ticker_from_history:
                # Проверяем, похож ли текущий вопрос на уточняющий
                clarification_keywords = ["объем", "цена", "он", "она", "его", "ее", "это", "тикер", "акция", "бумага", "инструмент", "график", "уровень", "сколько стоит", "как там", "что там"]
                # Добавим проверку на короткую длину вопроса (часто уточнения короткие)
                is_clarifying_question = len(user_message) < 50 or any(keyword in user_message.lower() for keyword in clarification_keywords)

                if is_clarifying_question:
                    logger.info(f"Текущий вопрос '{user_message[:50]}...' похож на уточняющий по тикеру '{ticker_from_history}' из истории.")
                    ticker_context = ticker_from_history
                else:
                    logger.info(f"Вопрос не похож на уточняющий, тикер '{ticker_from_history}' из истории игнорируется.")

    # Если мы определили контекстный тикер (из сообщения или истории), получаем котировку
    if ticker_context:
        logger.info(f"Запрашиваем котировку для контекстного тикера: {ticker_context}")
        quote_data_to_use = await get_moex_quote(ticker_context) # quote_data_to_use будет или словарем, или None
        if quote_data_to_use:
             logger.info(f"Котировка для {ticker_context} успешно получена (или взята из кеша).")
        else:
             logger.warning(f"Не удалось получить котировку для контекстного тикера {ticker_context}.")


    # --- Шаг 3: Формирование ЕДИНОГО начального контекстного блока ---
    initial_context_parts = []
    initial_context_parts.append(ELDER_TEXT_PROMPT) # Системный промпт
    initial_context_parts.append(context_from_books_str) # RAG

    # Добавляем котировки и инструкцию ТОЛЬКО ЕСЛИ они были успешно получены
    if quote_data_to_use:
        initial_context_parts.append("\n\n--- Current Market Data (provided by the system) ---")
        # Форматируем данные здесь
        ticker = quote_data_to_use.get('SECID', ticker_context or 'N/A') # Используем ticker_context как фолбэк
        change_percent = quote_data_to_use.get('LASTTOPREVPRICE')
        change_sign = "+" if change_percent is not None and change_percent > 0 else ""
        change_str = f"{change_sign}{change_percent:.2f}%" if change_percent is not None else "N/A"
        vol_today = quote_data_to_use.get('VOLTODAY')
        vol_str = f"{vol_today:,}".replace(',', ' ') if vol_today is not None else "N/A"
        quote_str = (
            f"{quote_data_to_use.get('SECNAME', ticker)} ({ticker}): "
            f"Price={quote_data_to_use.get('LAST', 'N/A')} RUB ({change_str}), "
            f"Volume={vol_str} pcs."
        )
        initial_context_parts.append(quote_str)
        initial_context_parts.append("--- End of Market Data ---")
        initial_context_parts.append("\n**Instruction:** Please actively use the provided book excerpts AND the market data above when formulating your response.")
        logger.info(f"Добавлен контекст котировок для {ticker} в начальный контекст.")
    elif ticker_context and not quote_data_to_use:
        # Если тикер был, но котировку не получили, сообщим модели об этом
         initial_context_parts.append(f"\n(Note: Failed to retrieve current market data for {ticker_context}.)\n")

    initial_user_content = "\n".join(initial_context_parts).strip()


    # --- Шаг 4: Формирование ПОЛНОЙ истории для API ---
    content_for_api = []
    content_for_api.append({'role': 'user', 'parts': [initial_user_content]})
    content_for_api.append({'role': 'model', 'parts': ["Understood. I am ready to answer as Dr. Alexander Elder, using all the provided context."]})

    if chat_history:
        content_for_api.extend(chat_history)
        logger.info(f"Добавлено {len(chat_history)} сообщений из истории в контент API.")

    content_for_api.append({'role': 'user', 'parts': [user_message]})


    # --- Шаг 5: Вызов Gemini API ---
    try:
        logger.info("Отправка V4 контента (Initial Context + History + Query) к Gemini...")
        log_content_preview = content_for_api[:2] + content_for_api[-3:]
        logger.debug(f"Структура V4 контента для Gemini API (Preview):\n{log_content_preview}")

        response = await text_model.generate_content_async(content_for_api, stream=False)

        # --- Обработка ответа (без изменений) ---
        final_response_text = None
        if response.parts:
             final_response_text = "".join(part.text for part in response.parts if hasattr(part, 'text')).strip()
             logger.info("Ответ от V4 Gemini получен через 'parts'.")
        elif hasattr(response, 'text') and response.text and response.text.strip():
             final_response_text = response.text.strip()
             logger.info("Ответ от V4 Gemini получен через 'text'.")
        elif response.prompt_feedback and response.prompt_feedback.block_reason:
             reason = response.prompt_feedback.block_reason.name
             logger.warning(f"Ответ Gemini V4 заблокирован. Причина: {reason}")
             if reason == "SAFETY": return "Sorry, I cannot answer this question due to content safety restrictions."
             elif reason == "OTHER": return "Sorry, I cannot answer this question due to an unspecified policy reason."
             else: return f"Could not get response from the text model. Block reason: {reason}."
        else:
             logger.error(f"Не удалось извлечь текст из V4 ответа Gemini. Response: {response}")
             return "Sorry, I could not get a structured response from the text model. Please try again later."

        if final_response_text:
             disclaimer = "\n\n---\n*Disclaimer: I am an AI simulating Dr. Alexander Elder...*" # Добавьте полный текст
             return final_response_text + disclaimer
        else:
             logger.error("Не удалось получить текст V4 ответа после всех проверок.")
             return "Sorry, an unexpected issue occurred while processing the response."

    except Exception as e:
        logger.error(f"Ошибка при взаимодействии с V4 Gemini: {e}", exc_info=True)
        return f"An internal error occurred while generating the text response ({type(e).__name__}). Please try again later."