FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание рабочей директории
WORKDIR /app

# Копирование requirements и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY . .

# Создание директории для загрузок
RUN mkdir -p downloads

# Команда по умолчанию
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
