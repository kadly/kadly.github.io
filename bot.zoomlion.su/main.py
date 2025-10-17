import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

app = FastAPI()

# Настройка CORS для разрешения запросов с вашего сайта
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене лучше указать конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    text: str
    sender: str

class ChatRequest(BaseModel):
    messages: List[Message]

@app.post("/api/chat")
async def chat_handler(chat_request: ChatRequest):
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if not API_KEY:
        print("ERROR: GOOGLE_API_KEY not found in .env")
        raise HTTPException(status_code=500, detail="API key not configured")

    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

    # Форматируем историю для Google API
    contents = []
    for msg in chat_request.messages:
        role = "model" if msg.sender == "bot" else "user"
        contents.append({"role": role, "parts": [{"text": msg.text}]})

    data = {"contents": contents}

    try:
        async with httpx.AsyncClient() as client:
            api_res = await client.post(API_URL, json=data, timeout=30.0)
            api_res.raise_for_status()  # Вызовет исключение для 4xx/5xx ответов
            
            response_data = api_res.json()
            bot_response = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Sorry, I could not get a response.")

            return {"reply": bot_response}

    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
