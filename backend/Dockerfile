# Dockerfile для Render.com с поддержкой faster-whisper
FROM python:3.11-slim

# Устанавливаем системные зависимости для ffmpeg и faster-whisper
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libavdevice-dev \
    libavfilter-dev \
    libswscale-dev \
    libswresample-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь код приложения
COPY . .

# Создаём директории для временных файлов
RUN mkdir -p /tmp/audio /tmp/video

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose порт
EXPOSE 8000

# Команда запуска
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
