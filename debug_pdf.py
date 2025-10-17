import os
import logging
from langchain_community.document_loaders import UnstructuredPDFLoader

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- КОНФИГУРАЦИЯ ---
# Указываем путь к конкретному проблемному файлу
PDF_PATH = os.path.join("books", "MAZ ZMC-25  - Техническое описание.pdf")
# -------------------

def debug_document(file_path):
    """Загружает один PDF и выводит на экран извлеченные элементы."""
    if not os.path.exists(file_path):
        logging.error(f"Файл не найден: {file_path}")
        return

    try:
        logging.info(f"Загрузка PDF (Unstructured, hi_res): {os.path.basename(file_path)}")
        # Используем те же настройки, что и в скрипте индексации
        loader = UnstructuredPDFLoader(
            file_path,
            mode="elements",
            strategy="hi_res",
            languages=["rus"]
        )
        documents = loader.load()

        logging.info(f"--- Найдено {len(documents)} элементов в документе ---")
        for i, doc in enumerate(documents):
            page_num = doc.metadata.get('page_number', 'N/A')
            element_type = doc.metadata.get('category', 'Unknown')
            print("-" * 80)
            print(f"Элемент {i+1} | Тип: {element_type} | Страница: {page_num}")
            print("-" * 80)
            print(doc.page_content)
            print("\n")

    except Exception as e:
        logging.error(f"Ошибка при обработке файла {file_path}: {e}")

if __name__ == '__main__':
    debug_document(PDF_PATH)
