import os
from dotenv import load_dotenv
import chromadb
# Убираем импорт embedding_functions, он больше не нужен здесь
# from chromadb.utils import embedding_functions
import PyPDF2
import logging
import re
import sys
import time # Для задержки между запросами

# --- НОВЫЙ ИМПОРТ ---
import google.generativeai as genai

# --- Конфигурация ---
BOOKS_DIR = "/root/bots/elderabot/books" # Пример, используйте ваш путь
CHROMA_DATA_PATH = "chroma_db_data"
COLLECTION_NAME = "elder_books"
EMBEDDING_MODEL_NAME = 'models/embedding-001' # Используемая модель эмбеддингов
# Уменьшаем размер чанка ЕЩЕ СИЛЬНЕЕ на всякий случай, т.к. ручное управление
CHUNK_SIZE_CHARS = 4000
CHUNK_OVERLAP_CHARS = 100
# Размер батча для Google API (сколько чанков отправлять за раз)
GOOGLE_API_BATCH_SIZE = 5 # Попробуем небольшое значение
# Задержка между запросами к Google API (в секундах), чтобы не превысить лимиты QPS
API_CALL_DELAY = 1.1 # Немного больше 1 секунды (лимит часто 60 запросов/минуту)

# Загрузка ключа из .env
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logging.error("Не найден GEMINI_API_KEY в .env файле или переменных окружения.")
    exit()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Инициализация Google Gemini API ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # НЕ модель для генерации, а именно для эмбеддингов (хотя API может быть общим)
    # Используем сам модуль genai для вызова embed_content
    logging.info(f"Google Generative AI SDK сконфигурирован для модели {EMBEDDING_MODEL_NAME}.")
except Exception as e:
    logging.error(f"Ошибка конфигурации Google Generative AI SDK: {e}", exc_info=True)
    exit()


# --- Функции extract_text_from_pdf, split_into_chunks, clean_text ---
# Оставляем их как в предыдущей версии (split_into_chunks уже улучшенная)
# Убедитесь, что split_into_chunks использует CHUNK_SIZE_CHARS и CHUNK_OVERLAP_CHARS

# --- Функция извлечения текста (пример для PDF) ---
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file, strict=False)
            logging.info(f"Читаем {len(reader.pages)} страниц из {os.path.basename(pdf_path)}...")
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as page_e:
                    logging.warning(f"Ошибка извлечения текста со страницы {i+1} файла {os.path.basename(pdf_path)}: {page_e}")
            logging.info(f"Извлечен текст из {os.path.basename(pdf_path)}, примерный размер: {len(text)} символов")
        return text
    except Exception as e:
        logging.error(f"Ошибка при чтении PDF {pdf_path}: {e}", exc_info=True)
        return None

# --- Улучшенная функция разбивки на чанки ---
def split_into_chunks(text, chunk_size_chars=CHUNK_SIZE_CHARS, chunk_overlap_chars=CHUNK_OVERLAP_CHARS):
    if not text: return []
    chunks = []
    current_pos = 0
    text_len = len(text)
    logging.info(f"Начало разбивки текста длиной {text_len} символов на чанки размером ~{chunk_size_chars} с перекрытием {chunk_overlap_chars}")
    while current_pos < text_len:
        end_pos = min(current_pos + chunk_size_chars, text_len)
        chunk = text[current_pos:end_pos]
        chunks.append(chunk)
        logging.debug(f"Создан чанк: позиция {current_pos}-{end_pos}, символов: {len(chunk)}")
        if end_pos == text_len: break
        next_start_pos = max(0, end_pos - chunk_overlap_chars)
        if next_start_pos <= current_pos: next_start_pos = current_pos + 1
        current_pos = next_start_pos
    num_chunks = len(chunks)
    if num_chunks > 0:
      avg_len = sum(len(c) for c in chunks) / num_chunks
      logging.info(f"Текст разбит на {num_chunks} чанков. Средняя длина: {avg_len:.0f} символов.")
    else:
      logging.warning("Не удалось создать ни одного чанка из текста.")
    chunks = [chunk for chunk in chunks if chunk.strip()]
    return chunks

# --- Функция очистки текста (базовая) ---
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# --- Основная логика ---
if __name__ == "__main__":
    # 1. Найти книги
    if not os.path.exists(BOOKS_DIR): logging.error(f"Папка с книгами не найдена: {BOOKS_DIR}"); exit()
    book_files = [os.path.join(BOOKS_DIR, f) for f in os.listdir(BOOKS_DIR) if f.lower().endswith('.pdf')]
    if not book_files: logging.error(f"Не найдены PDF файлы в папке: {BOOKS_DIR}"); exit()

    # 2. Инициализировать ChromaDB КЛИЕНТА (БЕЗ embedding_function!)
    try:
        chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
        # НЕ указываем embedding_function, так как будем передавать векторы сами
        collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
        logging.info(f"ChromaDB коллекция '{COLLECTION_NAME}' готова (ожидает ручной передачи эмбеддингов).")
    except Exception as e:
         logging.error(f"Ошибка инициализации ChromaDB Client: {e}", exc_info=True)
         exit()

    all_chunks_data = []
    # 3. Обработать книги и получить ВСЕ чанки
    for book_path in book_files:
        logging.info(f"Обработка книги: {book_path}...")
        raw_text = extract_text_from_pdf(book_path)
        if not raw_text: logging.warning(f"Не удалось извлечь текст из {os.path.basename(book_path)}, пропускаем."); continue
        cleaned_text = clean_text(raw_text)
        chunks = split_into_chunks(cleaned_text) # Использует CHUNK_SIZE_CHARS
        book_name = os.path.basename(book_path)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{book_name}_chunk_{i}"
            all_chunks_data.append({
                "id": chunk_id,
                "document": chunk,
                "metadata": {"source": book_name, "chunk_index": i}
            })
    logging.info(f"Всего подготовлено {len(all_chunks_data)} чанков для вычисления эмбеддингов.")

    # --- 4. ВЫЧИСЛЕНИЕ ЭМБЕДДИНГОВ БАТЧАМИ через Google API ---
    all_embeddings = []
    num_chunks_total = len(all_chunks_data)
    num_batches = (num_chunks_total + GOOGLE_API_BATCH_SIZE - 1) // GOOGLE_API_BATCH_SIZE

    logging.info(f"Начинаем вычисление эмбеддингов для {num_chunks_total} чанков батчами по {GOOGLE_API_BATCH_SIZE}...")

    for i in range(num_batches):
        start_idx = i * GOOGLE_API_BATCH_SIZE
        end_idx = min((i + 1) * GOOGLE_API_BATCH_SIZE, num_chunks_total)
        current_batch_chunks_data = all_chunks_data[start_idx:end_idx]
        # Извлекаем только текст чанков для отправки в API
        batch_texts = [item["document"] for item in current_batch_chunks_data]

        logging.info(f"Обработка батча {i+1}/{num_batches} ({len(batch_texts)} чанков): Индексы {start_idx}-{end_idx-1}")

        try:
            # Вызов Google API для получения эмбеддингов
            # task_type="RETRIEVAL_DOCUMENT" важен для RAG
            result = genai.embed_content(
                model=EMBEDDING_MODEL_NAME,
                content=batch_texts,
                task_type="RETRIEVAL_DOCUMENT" # Указываем, что это документы для поиска
                )

            # Проверяем, что результат содержит эмбеддинги и их количество совпадает
            if 'embedding' in result and len(result['embedding']) == len(batch_texts):
                batch_embeddings = result['embedding']
                all_embeddings.extend(batch_embeddings)
                logging.info(f"Батч {i+1}/{num_batches}: Успешно получено {len(batch_embeddings)} эмбеддингов.")
            else:
                logging.error(f"Батч {i+1}/{num_batches}: Неожиданный формат ответа от Google API или неверное кол-во эмбеддингов. Ответ: {result}")
                # Можно добавить логику остановки или пропуска батча
                # Пока просто добавляем None, чтобы не сломать дальнейшую логику, но это плохо
                all_embeddings.extend([None] * len(batch_texts))


            # Задержка перед следующим запросом к API
            if i < num_batches - 1: # Не делаем задержку после последнего батча
                 logging.debug(f"Задержка на {API_CALL_DELAY} сек перед следующим батчем...")
                 time.sleep(API_CALL_DELAY)

        except Exception as e:
            logging.error(f"Ошибка при вычислении эмбеддингов для батча {i+1}/{num_batches} (Индексы {start_idx}-{end_idx-1}): {e}", exc_info=True)
            # Добавляем None для пропущенных эмбеддингов
            all_embeddings.extend([None] * len(batch_texts))
            # Можно добавить более умную обработку ошибок, например, повторную попытку

    # Проверка, что у нас есть эмбеддинги для всех чанков (хотя бы None)
    if len(all_embeddings) != num_chunks_total:
        logging.error(f"Критическая ошибка: количество полученных эмбеддингов ({len(all_embeddings)}) не совпадает с количеством чанков ({num_chunks_total}). Прерывание.")
        exit()

    # --- 5. ДОБАВЛЕНИЕ ДАННЫХ С ГОТОВЫМИ ЭМБЕДДИНГАМИ в ChromaDB ---
    logging.info("Начинаем добавление данных с вычисленными эмбеддингами в ChromaDB...")
    added_count = 0
    skipped_count = 0
    failed_count = 0

    # Можно добавлять большими батчами, т.к. эмбеддинги уже есть
    chroma_batch_size = 100
    num_chroma_batches = (num_chunks_total + chroma_batch_size - 1) // chroma_batch_size

    for i in range(num_chroma_batches):
        start_idx = i * chroma_batch_size
        end_idx = min((i + 1) * chroma_batch_size, num_chunks_total)

        # Собираем данные для батча ChromaDB
        batch_ids = []
        batch_documents = []
        batch_metadatas = []
        batch_embeddings_final = [] # Только валидные эмбеддинги

        for j in range(start_idx, end_idx):
            chunk_data = all_chunks_data[j]
            embedding = all_embeddings[j]
            if embedding is not None: # Добавляем только если эмбеддинг был успешно вычислен
                batch_ids.append(chunk_data["id"])
                batch_documents.append(chunk_data["document"])
                batch_metadatas.append(chunk_data["metadata"])
                batch_embeddings_final.append(embedding)
            else:
                logging.warning(f"Пропуск чанка ID={chunk_data['id']}, так как для него не удалось вычислить эмбеддинг.")
                skipped_count += 1

        # Добавляем батч в ChromaDB, если в нем есть валидные данные
        if batch_ids:
            logging.info(f"Добавление батча {i+1}/{num_chroma_batches} ({len(batch_ids)} чанков) в ChromaDB...")
            try:
                collection.add(
                    ids=batch_ids,
                    documents=batch_documents,
                    metadatas=batch_metadatas,
                    embeddings=batch_embeddings_final # <--- ПЕРЕДАЕМ ГОТОВЫЕ ЭМБЕДДИНГИ
                )
                added_count += len(batch_ids)
                logging.debug(f"Батч {i+1}/{num_chroma_batches} успешно добавлен.")
            except Exception as e:
                failed_count += len(batch_ids)
                logging.error(f"Ошибка при добавлении батча {i+1}/{num_chroma_batches} в ChromaDB: {e}", exc_info=True)
        else:
             logging.info(f"Батч {i+1}/{num_chroma_batches} пуст (все эмбеддинги были None), пропускаем добавление в ChromaDB.")


    logging.info(f"Добавление в ChromaDB завершено. Успешно добавлено: {added_count}, Пропущено (ошибка эмбеддинга): {skipped_count}, Ошибок при добавлении в ChromaDB: {failed_count}")
    logging.info("Скрипт предварительной обработки завершен.")