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
    fontconfig \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Создаём директорию для шрифтов
RUN mkdir -p /usr/share/fonts/truetype/custom

# Копируем шрифт Impact если есть (положите impact.ttf в backend/fonts/)
# Если файла нет - будет использован Arial Bold из fonts-liberation
COPY fonts/impact.ttf /usr/share/fonts/truetype/custom/impact.ttf || true

# Обновляем кэш шрифтов
RUN fc-cache -fv

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
