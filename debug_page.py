import os
import logging
import fitz  # PyMuPDF

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- КОНФИГУРАЦИЯ ---
TARGET_FILE = "MAZ ZMC-25  - Техническое описание.pdf"
TARGET_PAGE = 1  # Страницы нумеруются с 1
# -------------------

def inspect_page():
    """
    Извлекает и печатает текст с одной конкретной страницы PDF-файла.
    """
    file_path = os.path.join("books", TARGET_FILE)
    if not os.path.exists(file_path):
        print(f"Ошибка: Файл не найден: {file_path}")
        return

    try:
        print(f"--- Чтение страницы {TARGET_PAGE} из файла: {TARGET_FILE} ---")
        doc = fitz.open(file_path)
        
        # PyMuPDF нумерует страницы с 0, поэтому вычитаем 1
        if 0 <= TARGET_PAGE - 1 < len(doc):
            page = doc[TARGET_PAGE - 1]
            text = page.get_text("text")
            
            print("-" * 80)
            print("ИЗВЛЕЧЕННЫЙ ТЕКСТ:")
            print("-" * 80)
            print(text)
            print("-" * 80)
            
        else:
            print(f"Ошибка: В документе нет страницы с номером {TARGET_PAGE}. Всего страниц: {len(doc)}")
            
        doc.close()

    except Exception as e:
        print(f"\nПроизошла ошибка: {e}")

if __name__ == '__main__':
    inspect_page()
