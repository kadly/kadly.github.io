import os
import logging
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser

# Загружаем переменные окружения из .env файла
load_dotenv()

# Проверяем, что ключ API загружен
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("Не найден GOOGLE_API_KEY. Пожалуйста, добавьте его в ваш .env файл.")

# Настройка логирования
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# --- КОНФИГУРАЦИЯ ---
DB_PATH = "db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
# -------------------

ANSWER_PROMPT_TEMPLATE = """
Ты — ИИ-консультант сайта zoomlion.su. Твоя задача — помочь пользователям, отвечая на вопросы о строительной технике Zoomlion, используя предоставленный контекст из внутренней базы знаний.

Проанализируй следующий контекст. На его основе составь полный и структурированный ответ на запрос пользователя.

- Всегда веди диалог от лица официального консультанта zoomlion.su.
- Если пользователь ищет технику по параметрам (например, "мне нужен кран 25 тонн" или "информация по крану ZTC250V"), твоя задача — подробно описать подходящие модели из контекста. Систематизируй и перечисли их ключевые технические характеристики.
- Если в контексте нет точной информации для ответа, сообщи, что не удалось найти данные по этому запросу в базе, но ты можешь помочь с информацией по другому ассортименту. Не выдумывай технические характеристики.
- Ответ должен быть на русском языке, структурированным и понятным для клиента.

Контекст:
{context}

Запрос пользователя:
{question}

Ответ:
"""

# Новый промпт для извлечения фильтров
FILTER_EXTRACTION_TEMPLATE = """
Твоя задача - извлечь из вопроса пользователя фильтры для поиска по базе данных и основной поисковый запрос.
Ответь в формате JSON с двумя ключами: 'query' (основной запрос) и 'filter' (фильтр).

Пользовательский вопрос: "{question}"

Доступные поля для фильтрации:
- lifting_capacity_tons (float): Грузоподъемность в тоннах.
- source (string): Источник информации (путь к файлу).

Правила для фильтрации:
- Если в вопросе есть упоминание грузоподъемности, создай фильтр.
- Используй операторы '$eq' (равно), '$ne' (не равно), '$gt' (больше), '$gte' (больше или равно), '$lt' (меньше), '$lte' (меньше или равно).
- Фильтр должен быть словарем, где ключ - это поле, а значение - это словарь с оператором и значением. Например: {{"lifting_capacity_tons": {{"$gte": 100}} }}
- Если фильтров нет, оставь значение для ключа 'filter' пустым объектом {{}}.
- В 'query' помести оригинальный вопрос, возможно, слегка упрощенный, но сохранивший основной смысл.

Примеры:
Вопрос: "Что известно о кране грузоподъемностью 120 тонн?"
Ответ: {{"query": "кран грузоподъемностью 120 тонн", "filter": {{"lifting_capacity_tons": {{"$eq": 120.0}}}} }}

Вопрос: "Какие есть краны от MAZ?"
Ответ: {{"query": "краны MAZ", "filter": {{}} }}

Вопрос: "Найди документы про ZAT1200V грузоподъемностью больше 100 тонн"
Ответ: {{"query": "ZAT1200V", "filter": {{"lifting_capacity_tons": {{"$gt": 100.0}}}} }}

Теперь твой черед.

Пользовательский вопрос: "{question}"
Ответ (только JSON):
"""

def main():
    """
    Основная функция для общения с RAG-системой.
    """
    if not os.path.exists(DB_PATH):
        print(f"Ошибка: База данных в папке '{DB_PATH}' не найдена.")
        print("Пожалуйста, сначала запустите скрипт '1_index_books.py' для создания базы.")
        return

    # 1. Загрузка эмбеддингов и векторной базы
    print("Загрузка модели эмбеддингов и базы данных...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    print("Загрузка завершена.")

    # 2. Настройка LLM (Gemini)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

    # 3. Цепочка для извлечения фильтров
    filter_prompt = PromptTemplate.from_template(FILTER_EXTRACTION_TEMPLATE)
    filter_chain = filter_prompt | llm | StrOutputParser()

    # 4. Цепочка для генерации ответа
    answer_prompt = PromptTemplate(template=ANSWER_PROMPT_TEMPLATE, input_variables=["context", "question"])
    answer_chain = LLMChain(llm=llm, prompt=answer_prompt)
    
    # 5. Цикл вопросов и ответов
    print("\n--- ИИ-помощник по строительной технике готов ---")
    print("Введите ваш вопрос. Для выхода напишите 'выход' или 'exit'.")

    while True:
        query = input("\nВаш вопрос: ")
        if query.lower() in ['выход', 'exit']:
            break
        if not query.strip():
            continue

        try:
            # Этап 1: Извлечение фильтров
            print("Анализ вопроса...")
            filter_json_str = filter_chain.invoke({"question": query})
            
            try:
                if filter_json_str.strip().startswith("```json"):
                    filter_json_str = filter_json_str.strip()[7:-3].strip()
                filter_data = json.loads(filter_json_str)
                search_query = filter_data.get("query", query)
                search_filter = filter_data.get("filter")
            except json.JSONDecodeError:
                print("Не удалось извлечь фильтр, будет выполнен поиск по всему вопросу.")
                search_query = query
                search_filter = None

            # Этап 2: Поиск документов
            print(f"Поиск по запросу: '{search_query}' с фильтром: {search_filter}...")
            retriever = vectorstore.as_retriever(
                search_type="mmr",
                search_kwargs={
                    'filter': search_filter if search_filter else {},
                    'k': 20, # Увеличиваем количество извлекаемых документов
                    'fetch_k': 50 # Количество документов для первоначального отбора
                }
            )
            final_docs = retriever.invoke(search_query)

            if not final_docs:
                print("\n--- Ответ ---")
                print("К сожалению, по вашему запросу ничего не найдено.")
                continue

            # Этап 3: Генерация ответа
            context_parts = []
            for doc in final_docs:
                source = os.path.basename(doc.metadata.get('source', 'Неизвестный источник'))
                content = doc.page_content
                context_parts.append(f"Контекст из файла '{source}':\n---\n{content}\n---")
            
            full_context = "\n\n".join(context_parts)
            result = answer_chain.invoke({"context": full_context, "question": query})
            
            print("\n--- Ответ ---")
            print(result["text"])
            
            print("\n--- Источники ---")
            unique_sources = set()
            for doc in final_docs:
                source = doc.metadata.get('source', 'Неизвестный источник')
                page_num = doc.metadata.get('page')
                page_str = f"Страница: {page_num}" if page_num is not None else "Страница: N/A"
                source_info = f"  - Источник: {os.path.basename(source)}, {page_str}"
                unique_sources.add(source_info)
            
            for source_info in sorted(list(unique_sources)):
                 print(source_info)

        except Exception as e:
            print(f"\nПроизошла ошибка: {e}")

if __name__ == '__main__':
    main()