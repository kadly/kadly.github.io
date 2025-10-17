import os
import logging
import re
import shutil
import json
from collections import defaultdict
from unstructured.partition.pdf import partition_pdf
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- КОНФИГУРАЦИЯ ---
# Пути внутри контейнера, куда будет смонтирован Google Drive
BOOKS_PATH = "/gdrive_data/books"
SITE_DATA_PATH = "/gdrive_data/src/data"
DB_PATH = "db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# -------------------

def extract_lifting_capacity(text):
    """
    Извлекает числовое значение грузоподъемности из текста.
    """
    patterns = [
        r"грузоподъемность[^
]*(\d+([.,]\d+)?)",
        r"(\d+([.,]\d+)?)\s*т\b"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                capacity_str = match.group(1).replace(',', '.')
                return float(capacity_str)
            except (ValueError, IndexError):
                continue
    return None

def load_books_as_pages(path):
    """
    Загружает PDF из папки 'books', группирует элементы по страницам.
    """
    page_docs = []
    if not os.path.exists(path):
        logging.warning(f"Папка с книгами '{path}' не найдена. Пропускаем.")
        return page_docs

    for filename in os.listdir(path):
        if not filename.lower().endswith('.pdf'):
            continue
            
        file_path = os.path.join(path, filename)
        try:
            logging.info(f"Обработка PDF-файла: {filename}...")
            elements = partition_pdf(
                file_path, 
                strategy="hi_res", 
                infer_table_structure=True,
                model_name="yolox",
                languages=['rus']
            )
            
            full_text = " ".join([el.text for el in elements if el.text])
            capacity = extract_lifting_capacity(full_text)
            if capacity:
                logging.info(f"  -> Найдена общая грузоподъемность для файла: {capacity} тонн")

            pages = defaultdict(str)
            for el in elements:
                if el.text:
                    pages[el.metadata.page_number] += el.text + "\n\n"

            logging.info(f"  -> Найдено {len(pages)} страниц в документе.")
            for page_num, page_content in pages.items():
                metadata = {
                    "source": file_path,
                    "page": page_num,
                    "type": "book" # Добавляем тип источника
                }
                if capacity is not None:
                    metadata["lifting_capacity_tons"] = capacity
                
                page_docs.append(Document(page_content=page_content, metadata=metadata))

        except Exception as e:
            logging.error(f"Ошибка при обработке файла {filename}: {e}", exc_info=True)
    return page_docs

def load_site_data(path):
    """
    Загружает данные о продуктах из JSON-файлов в 'src/data'.
    """
    product_docs = []
    if not os.path.exists(path):
        logging.warning(f"Папка с данными сайта '{path}' не найдена. Пропускаем.")
        return product_docs

    for filename in os.listdir(path):
        if not filename.lower().endswith('.json'):
            continue
        
        file_path = os.path.join(path, filename)
        logging.info(f"Обработка JSON-файла: {filename}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                for product in data:
                    title = product.get("name", "Без названия")
                    description = product.get("description", "")
                    specifications = product.get("details", [])
                    
                    content_parts = [f"Название модели: {title}"]
                    if description:
                        content_parts.append(f"Описание: {description}")
                    
                    capacity = None
                    if specifications:
                        content_parts.append("\nТехнические характеристики:")
                        for spec in specifications:
                            prop = spec.get('label', '')
                            val = spec.get('value', '')
                            content_parts.append(f"- {prop}: {val}")
                            if "грузоподъемность" in prop.lower() and not capacity:
                                capacity_text = extract_lifting_capacity(f"{prop} {val}")
                                if capacity_text:
                                    capacity = capacity_text

                    full_content = "\n".join(content_parts)
                    
                    metadata = {
                        "source": file_path,
                        "model": title,
                        "type": "product"
                    }
                    if capacity:
                        metadata["lifting_capacity_tons"] = capacity

                    product_docs.append(Document(page_content=full_content, metadata=metadata))
            logging.info(f"  -> Загружено {len(data)} продуктов из {filename}.")

        except Exception as e:
            logging.error(f"Ошибка при обработке файла {filename}: {e}", exc_info=True)
            
    return product_docs


def main():
    """
    Основная функция для индексации всех документов.
    """
    logging.info("--- Этап 1: Загрузка документов ---")
    book_pages = load_books_as_pages(BOOKS_PATH)
    site_products = load_site_data(SITE_DATA_PATH)
    
    all_documents = book_pages + site_products
    if not all_documents:
        logging.warning("Документы для индексации не найдены.")
        return
    logging.info(f"Всего для обработки: {len(book_pages)} страниц из книг и {len(site_products)} продуктов с сайта.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        chunk_overlap=400,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    book_chunks = text_splitter.split_documents(book_pages)
    
    final_chunks = book_chunks + site_products
    logging.info(f"Создано {len(final_chunks)} итоговых фрагментов для индексации.")

    logging.info("--- Этап 2: Создание эмбеддингов и сохранение в базу данных ---")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    if os.path.exists(DB_PATH):
        logging.info(f"Удаление старой базы данных в '{DB_PATH}'...")
        shutil.rmtree(DB_PATH)

    vectorstore = Chroma.from_documents(
        documents=final_chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    
    logging.info("--- Процесс индексации успешно завершен! ---")

if __name__ == '__main__':
    main()