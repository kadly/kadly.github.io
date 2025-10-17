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

# --- Загрузка конфигурации и моделей ---
load_dotenv()
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("Не найден GOOGLE_API_KEY.")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DB_PATH = "/app/db"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"База данных в '{DB_PATH}' не найдена.")

logging.info("Загрузка моделей...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
logging.info("Модели загружены.")

# --- Старые промпты ---
ANSWER_PROMPT_TEMPLATE = """
Ты — ИИ-помощник, отвечающий на вопросы о строительной технике, используя предоставленный контекст.
Твоя задача — помочь пользователю, предоставив исчерпывающую информацию из найденных документов.
Если в контексте нет релевантной информации для ответа, просто скажи, что не можешь найти информацию по этому запросу. Не выдумывай ответ.
Отвечай на русском языке.

Контекст:
{context}

Запрос пользователя:
{question}

Ответ:
"""

# --- API ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        # Простой поиск по сходству
        retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={'k': 10})
        final_docs = retriever.invoke(query)

        if not final_docs:
            return AnswerResponse(answer="К сожалению, по вашему запросу ничего не найдено.", sources=[])

        # Генерация ответа
        answer_prompt = PromptTemplate(template=ANSWER_PROMPT_TEMPLATE, input_variables=["context", "question"])
        answer_chain = LLMChain(llm=llm, prompt=answer_prompt)
        
        context = "\n\n".join([doc.page_content for doc in final_docs])
        result = answer_chain.invoke({"context": context, "question": query})
        
        sources = sorted(list(set(os.path.basename(doc.metadata.get("source", "N/A")) for doc in final_docs)))

        return AnswerResponse(answer=result["text"], sources=sources)

    except Exception as e:
        logging.error(f"Ошибка: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Внутренняя ошибка.")

@app.get("/")
def read_root():
    return {"status": "API старой версии бота работает"}
