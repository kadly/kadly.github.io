# Этап 1: Установка системных зависимостей
FROM python:3.11-slim AS base

# Устанавливаем системные пакеты, необходимые для unstructured
RUN apt-get update && apt-get install -y \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Этап 2: Установка Python-зависимостей
FROM base AS builder

WORKDIR /install
COPY requirements.txt .
RUN pip install --prefix="/install" -r requirements.txt

# Этап 3: Финальный образ
FROM base

WORKDIR /app

# Копируем установленные пакеты из builder
COPY --from=builder /install /usr/local

# Копируем код приложения
COPY main.py .
# Копируем .env файл, если он есть в этой папке
COPY .env .

# Запускаем API сервер
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]