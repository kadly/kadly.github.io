import google.generativeai as genai
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Проверяем, что ключ API загружен
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Не найден GOOGLE_API_KEY. Пожалуйста, добавьте его в ваш .env файл.")

# Конфигурируем библиотеку с вашим ключом
genai.configure(api_key=api_key)

print("--- Доступные модели Gemini ---")

# Получаем и выводим список моделей
try:
    for model in genai.list_models():
        # Выводим только модели, которые поддерживают генерацию контента
        if 'generateContent' in model.supported_generation_methods:
            print(model.name)
except Exception as e:
    print(f"Произошла ошибка при запросе списка моделей: {e}")

print("\n--- Конец списка ---")
print("Пожалуйста, скопируйте точное имя модели из этого списка и используйте его в скрипте '2_ask_question.py'.")
