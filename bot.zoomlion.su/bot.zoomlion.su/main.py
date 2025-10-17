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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Загрузка конфигурации и моделей (выполняется один раз при старте) ---

load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("Не найден GOOGLE_API_KEY. Пожалуйста, добавьте его в ваш .env файл.")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = "/app/db" # Путь внутри Docker-контейнера
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Проверка существования базы данных
if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"База данных в '{DB_PATH}' не найдена. Убедитесь, что вы запустили индексацию и папка db находится в /root/bot.zoomlion.su/")

# Загрузка моделей
logging.info("Загрузка модели эмбеддингов...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
logging.info("Загрузка векторной базы данных...")
vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
logging.info("Загрузка LLM (Gemini)...")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

# --- Шаблоны промптов и цепочки ---

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

FILTER_EXTRACTION_TEMPLATE = """
Твоя задача - извлечь из вопроса пользователя фильтры для поиска по базе данных и основной поисковый запрос.
Ответь в формате JSON с двумя ключами: 'query' (основной запрос) и 'filter' (фильтр).
Пользовательский вопрос: "{question}"
Доступные поля для фильтрации:
- lifting_capacity_tons (float): Грузоподъемность в тоннах.
- source (string): Источник информации (путь к файлу).
Правила для фильтрации:
- Если в вопросе есть упоминание грузоподъемности, создай фильтр.
- Используй операторы '$eq', '$ne', '$gt', '$gte', '$lt', '$lte'.
- Фильтр должен быть словарем. Например: {{ "lifting_capacity_tons": {{ "$gte": 100 }} }}
- Если фильтров нет, оставь 'filter' пустым объектом {{}}.
- В 'query' помести оригинальный вопрос, возможно, слегка упрощенный.
Пользовательский вопрос: "{question}"
Ответ (только JSON):
"""

filter_prompt = PromptTemplate.from_template(FILTER_EXTRACTION_TEMPLATE)
filter_chain = filter_prompt | llm | StrOutputParser()

answer_prompt = PromptTemplate(template=ANSWER_PROMPT_TEMPLATE, input_variables=["context", "question"])
answer_chain = LLMChain(llm=llm, prompt=answer_prompt)

logging.info("Все модели и цепочки успешно загружены.")

# --- Определение API ---

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    query = request.question
    if not query.strip():
        raise HTTPException(status_code=400, detail="Вопрос не может быть пустым.")

    try:
        # 1. Извлечение фильтров
        filter_json_str = filter_chain.invoke({"question": query})
        try:
            if filter_json_str.strip().startswith("```json"):
                filter_json_str = filter_json_str.strip()[7:-3].strip()
            filter_data = json.loads(filter_json_str)
            search_query = filter_data.get("query", query)
            search_filter = filter_data.get("filter")
        except json.JSONDecodeError:
            search_query = query
            search_filter = None

        # 2. Поиск документов
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={'filter': search_filter if search_filter else {}, 'k': 20, 'fetch_k': 50}
        )
        final_docs = retriever.invoke(search_query)

        if not final_docs:
            return AnswerResponse(answer="К сожалению, по вашему запросу ничего не найдено в нашей базе.", sources=[])

        # 3. Генерация ответа
        context_parts = [f"Контекст из файла '{os.path.basename(doc.metadata.get('source', 'N/A'))}':\n---\n{doc.page_content}\n---" for doc in final_docs]
        full_context = "\n\n".join(context_parts)
        result = answer_chain.invoke({"context": full_context, "question": query})
        
        # 4. Сбор источников
        unique_sources = set()
        for doc in final_docs:
            source = os.path.basename(doc.metadata.get('source', 'Неизвестный источник'))
            model = doc.metadata.get('model')
            if model:
                unique_sources.add(f"Модель: {model} (источник: {source})")
            else:
                 unique_sources.add(f"Источник: {source}")

        return AnswerResponse(answer=result["text"], sources=sorted(list(unique_sources)))

    except Exception as e:
        logging.error(f"Ошибка при обработке запроса: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Произошла внутренняя ошибка.")

@app.get("/")
def read_root():
    return {"status": "API для Zoomlion-бота работает"}