import os
import logging
import re
import sys
import time
from dotenv import load_dotenv
import chromadb
import PyPDF2
import google.generativeai as genai

# --- НОВЫЕ ИМПОРТЫ для LlamaIndex ---
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document # Для представления текста перед сплиттером

# --- Конфигурация ---
# Укажите правильные пути
BOOKS_DIR = "/root/bots/elderabot/books"
CHROMA_DATA_PATH = "chroma_db_data" # Папка будет создана заново
COLLECTION_NAME = "elder_books"
EMBEDDING_MODEL_NAME = 'models/embedding-001'

# --- Параметры для SentenceSplitter ---
# Размер чанка теперь в *токенах* (примерно). Модель 'embedding-001' имеет лимит около 2048 токенов.
# Возьмем с запасом, например, 512 токенов на чанк.
CHUNK_SIZE_TOKENS = 512
# Перекрытие тоже в токенах
CHUNK_OVERLAP_TOKENS = 50
# Разделитель параграфов для более качественной первичной разбивки перед токенизацией
PARAGRAPH_SEPARATOR = "\n\n\n" # Используем тройной перенос как явный разделитель

# --- Параметры для Google API ---
GOOGLE_API_BATCH_SIZE = 5 # Сколько текстов чанков отправлять в Google API за раз
API_CALL_DELAY = 1.1 # Задержка между вызовами Google API

# --- Загрузка API ключа ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path): load_dotenv(dotenv_path)
else: load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY: logging.error("GEMINI_API_KEY не найден!"); exit()

# --- Настройка Логирования ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
# logging.getLogger('llama_index.core').setLevel(logging.DEBUG) # Для отладки LlamaIndex
logger = logging.getLogger(__name__)

# --- Инициализация Google Gemini API ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info(f"Google GenAI SDK сконфигурирован для модели {EMBEDDING_MODEL_NAME}.")
except Exception as e:
    logger.error(f"Ошибка конфигурации Google GenAI SDK: {e}", exc_info=True); exit()

# --- Функция извлечения текста из PDF (можно оставить прежнюю) ---
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file, strict=False)
            logger.info(f"Читаем {len(reader.pages)} страниц из {os.path.basename(pdf_path)}...")
            full_text_parts = []
            for i, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        full_text_parts.append(page_text.strip()) # Собираем текст страниц
                except Exception as page_e:
                    logging.warning(f"Ошибка извлечения текста со страницы {i+1} файла {os.path.basename(pdf_path)}: {page_e}")
            # Объединяем страницы через разделитель параграфов для SentenceSplitter
            text = PARAGRAPH_SEPARATOR.join(full_text_parts)
            logger.info(f"Извлечен текст из {os.path.basename(pdf_path)}, примерный размер: {len(text)} символов")
        return text
    except Exception as e:
        logger.error(f"Ошибка при чтении PDF {pdf_path}: {e}", exc_info=True)
        return None

# --- Функция очистки текста (можно оставить прежнюю) ---
def clean_text(text):
    # Убираем лишние пробелы, но сохраняем переносы строк для сплиттера
    text = re.sub(r'[ \t]+', ' ', text) # Заменяем множественные пробелы/табы на один пробел
    text = re.sub(r'\n +', '\n', text) # Убираем пробелы в начале строки после переноса
    text = re.sub(r' +\n', '\n', text) # Убираем пробелы в конце строки перед переносом
    text = re.sub(r'\n{3,}', PARAGRAPH_SEPARATOR, text) # Гарантируем наш разделитель параграфов
    return text.strip()

# --- Основная логика ---
if __name__ == "__main__":
    # 1. Найти книги
    if not os.path.exists(BOOKS_DIR): logging.error(f"Папка с книгами не найдена: {BOOKS_DIR}"); exit()
    book_files = [os.path.join(BOOKS_DIR, f) for f in os.listdir(BOOKS_DIR) if f.lower().endswith('.pdf')]
    if not book_files: logging.error(f"Не найдены PDF файлы в папке: {BOOKS_DIR}"); exit()
    logger.info(f"Найдено {len(book_files)} PDF файлов для обработки.")

    # 2. Инициализировать ChromaDB КЛИЕНТА и получить/создать коллекцию
    try:
        logger.info(f"Инициализация ChromaDB клиента в папке: {CHROMA_DATA_PATH}...")
        # Убедимся, что папка существует или будет создана
        if not os.path.exists(CHROMA_DATA_PATH):
             os.makedirs(CHROMA_DATA_PATH)
        chroma_client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
        # Получаем или создаем коллекцию БЕЗ embedding_function
        collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
        logger.info(f"ChromaDB коллекция '{COLLECTION_NAME}' готова.")
    except Exception as e:
         logger.error(f"Ошибка инициализации ChromaDB Client: {e}", exc_info=True); exit()

    # --- 3. Инициализация SentenceSplitter из LlamaIndex ---
    try:
        text_splitter = SentenceSplitter(
            chunk_size=CHUNK_SIZE_TOKENS,
            chunk_overlap=CHUNK_OVERLAP_TOKENS,
            paragraph_separator=PARAGRAPH_SEPARATOR,
            # separator=" ", # Разделитель по умолчанию
            # Можно указать модель для токенизации, если стандартная не подходит
            # tokenizer=tiktoken.get_encoding("cl100k_base") # Пример
        )
        logger.info(f"Инициализирован SentenceSplitter: chunk_size={CHUNK_SIZE_TOKENS} токенов, overlap={CHUNK_OVERLAP_TOKENS} токенов.")
    except Exception as e:
        logger.error(f"Ошибка инициализации SentenceSplitter: {e}. Убедитесь, что 'llama-index-core' установлен.", exc_info=True); exit()


    all_processed_chunks = [] # Список для хранения данных всех чанков перед эмбеддингом
    total_chunks_generated = 0

    # 4. Обработать книги, разбить новым сплиттером
    for book_path in book_files:
        logger.info(f"Обработка книги: {book_path}...")
        raw_text = extract_text_from_pdf(book_path)
        if not raw_text:
             logger.warning(f"Не удалось извлечь текст из {os.path.basename(book_path)}, пропускаем."); continue

        cleaned_text = clean_text(raw_text)
        book_name = os.path.basename(book_path)

        # Оборачиваем текст в Document LlamaIndex для передачи в сплиттер
        # document = Document(text=cleaned_text, metadata={"source": book_name}) # Можно так

        # Используем text_splitter для разбивки текста на чанки
        try:
            # split_text возвращает список строк
            chunks_texts = text_splitter.split_text(cleaned_text)
            num_book_chunks = len(chunks_texts)
            total_chunks_generated += num_book_chunks
            logger.info(f"Книга '{book_name}' разбита на {num_book_chunks} чанков с помощью SentenceSplitter.")

            # Сохраняем чанки с метаданными
            for i, chunk_text in enumerate(chunks_texts):
                chunk_id = f"{book_name}_chunk_{i}" # Уникальный ID чанка
                all_processed_chunks.append({
                    "id": chunk_id,
                    "document": chunk_text,
                    "metadata": {"source": book_name, "chunk_index": i}
                })
        except Exception as e:
            logger.error(f"Ошибка при разбивке текста из книги '{book_name}' сплиттером: {e}", exc_info=True)
            continue # Пропускаем книгу при ошибке разбивки

    logger.info(f"Всего подготовлено {total_chunks_generated} чанков из {len(book_files)} книг для вычисления эмбеддингов.")


    # --- 5. ВЫЧИСЛЕНИЕ ЭМБЕДДИНГОВ БАТЧАМИ (код остается прежним) ---
    all_embeddings = []
    num_chunks_total = len(all_processed_chunks) # Используем актуальное количество
    if num_chunks_total == 0:
        logger.warning("Нет чанков для обработки. Завершение."); exit()

    num_batches = (num_chunks_total + GOOGLE_API_BATCH_SIZE - 1) // GOOGLE_API_BATCH_SIZE
    logger.info(f"Начинаем вычисление эмбеддингов для {num_chunks_total} чанков батчами по {GOOGLE_API_BATCH_SIZE}...")

    for i in range(num_batches):
        start_idx = i * GOOGLE_API_BATCH_SIZE
        end_idx = min((i + 1) * GOOGLE_API_BATCH_SIZE, num_chunks_total)
        current_batch_chunks_data = all_processed_chunks[start_idx:end_idx]
        batch_texts = [item["document"] for item in current_batch_chunks_data]

        logging.info(f"Обработка батча {i+1}/{num_batches} ({len(batch_texts)} чанков): Индексы {start_idx}-{end_idx-1}")
        try:
            result = genai.embed_content(
                model=EMBEDDING_MODEL_NAME, content=batch_texts, task_type="RETRIEVAL_DOCUMENT"
            )
            if 'embedding' in result and len(result['embedding']) == len(batch_texts):
                batch_embeddings = result['embedding']
                all_embeddings.extend(batch_embeddings)
                logging.info(f"Батч {i+1}/{num_batches}: Успешно получено {len(batch_embeddings)} эмбеддингов.")
            else:
                logging.error(f"Батч {i+1}/{num_batches}: Неожиданный формат/кол-во эмбеддингов. Ответ: {result}")
                all_embeddings.extend([None] * len(batch_texts))

            if i < num_batches - 1:
                 logging.debug(f"Задержка на {API_CALL_DELAY} сек...")
                 time.sleep(API_CALL_DELAY)
        except Exception as e:
            logging.error(f"Ошибка при вычислении эмбеддингов для батча {i+1}/{num_batches}: {e}", exc_info=True)
            all_embeddings.extend([None] * len(batch_texts))

    if len(all_embeddings) != num_chunks_total:
        logging.error(f"Ошибка: кол-во эмбеддингов ({len(all_embeddings)}) != кол-ву чанков ({num_chunks_total})."); exit()


    # --- 6. ДОБАВЛЕНИЕ ДАННЫХ В ChromaDB (код остается прежним) ---
    logging.info("Начинаем добавление данных с эмбеддингами в ChromaDB...")
    added_count = 0; skipped_count = 0; failed_count = 0
    chroma_batch_size = 100 # Батч для добавления в ChromaDB
    num_chroma_batches = (num_chunks_total + chroma_batch_size - 1) // chroma_batch_size

    for i in range(num_chroma_batches):
        start_idx = i * chroma_batch_size
        end_idx = min((i + 1) * chroma_batch_size, num_chunks_total)
        batch_ids, batch_documents, batch_metadatas, batch_embeddings_final = [], [], [], []

        for j in range(start_idx, end_idx):
            chunk_data = all_processed_chunks[j]
            embedding = all_embeddings[j]
            if embedding is not None:
                batch_ids.append(chunk_data["id"])
                batch_documents.append(chunk_data["document"])
                batch_metadatas.append(chunk_data["metadata"])
                batch_embeddings_final.append(embedding)
            else:
                logging.warning(f"Пропуск чанка ID={chunk_data['id']} (ошибка эмбеддинга)."); skipped_count += 1

        if batch_ids:
            logging.info(f"Добавление батча {i+1}/{num_chroma_batches} ({len(batch_ids)} чанков) в ChromaDB...")
            try:
                collection.add(ids=batch_ids, documents=batch_documents, metadatas=batch_metadatas, embeddings=batch_embeddings_final)
                added_count += len(batch_ids); logging.debug(f"Батч {i+1}/{num_chroma_batches} успешно добавлен.")
            except Exception as e:
                failed_count += len(batch_ids); logging.error(f"Ошибка при добавлении батча {i+1}/{num_chroma_batches} в ChromaDB: {e}", exc_info=True)
        else:
             logging.info(f"Батч {i+1}/{num_chroma_batches} пуст, пропускаем добавление.")

    logging.info(f"Добавление в ChromaDB завершено. Успешно добавлено: {added_count}, Пропущено: {skipped_count}, Ошибок: {failed_count}")
    logging.info("Скрипт предварительной обработки завершен.")