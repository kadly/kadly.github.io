# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем системные зависимости
# Сначала обновляем списки и ставим ключи/сертификаты, потом снова обновляем и ставим остальное
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        debian-archive-keyring \
        apt-transport-https && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
# Обновляем pip и устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir --verbose -r requirements.txt

# Копируем остальной код проекта в рабочую директорию
COPY . .

# Указываем команду для запуска бота при старте контейнера
CMD ["python", "main.py"]