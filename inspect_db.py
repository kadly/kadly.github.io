import os
import logging
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Настройка логирования
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# --- КОНФИГУРАЦИЯ ---
DB_PATH = "db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# -------------------

def inspect_database():
    """
    Загружает векторную базу данных и выводит метаданные нескольких документов для проверки.
    """
    if not os.path.exists(DB_PATH):
        print(f"Ошибка: База данных в папке '{DB_PATH}' не найдена.")
        return

    print("Загрузка модели эмбеддингов и базы данных...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    print("Загрузка завершена.")

    print("\n--- Проверка метаданных в базе данных ---")
    
    # Получаем некоторое количество документов из базы
    results = vectorstore.get(include=["metadatas", "documents"], limit=20)
    
    metadatas = results.get('metadatas', [])
    documents = results.get('documents', [])
    
    if not metadatas:
        print("В базе данных не найдено документов для проверки.")
        return

    print(f"Найдено {len(metadatas)} документов. Вывод информации о них:\n")
    
    found_relevant = False
    for i, (metadata, doc_content) in enumerate(zip(metadatas, documents)):
        print(f"--- Документ {i+1} ---")
        source = metadata.get('source', 'N/A')
        print(f"Источник: {os.path.basename(source)}")
        print(f"Метаданные: {metadata}")
        print(f"Фрагмент текста: {doc_content[:200]}...")
        print("-" * 20)
        
        if "ZMC-25" in source:
            found_relevant = True

    if not found_relevant:
        print("\nПРЕДУПРЕЖДЕНИЕ: Среди первых 20 документов не найден файл, содержащий 'ZMC-25'.")
        print("Возможно, он не был проиндексирован или находится дальше в базе.")


if __name__ == '__main__':
    inspect_database()