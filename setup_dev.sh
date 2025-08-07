#!/bin/bash

# YouTube Video Downloader - Development Setup

echo "🚀 Настройка YouTube Video Downloader для разработки..."

# Создание виртуального окружения для backend
echo "📦 Создание виртуального окружения..."
cd backend
python -m venv venv

# Активация виртуального окружения
source venv/bin/activate

# Установка зависимостей
echo "📥 Установка Python зависимостей..."
pip install -r requirements.txt

# Создание .env файла
if [ ! -f .env ]; then
    echo "⚙️ Создание .env файла..."
    cp .env.example .env
fi

# Возврат в корневую директорию
cd ..

# Установка frontend зависимостей
echo "📥 Установка Frontend зависимостей..."
cd frontend
npm install
cd ..

echo "✅ Настройка завершена!"
echo ""
echo "Для запуска в режиме разработки:"
echo "1. Backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "2. Celery Worker: cd backend && source venv/bin/activate && celery -A app.tasks.celery_app worker --loglevel=info"
echo "3. Frontend: cd frontend && npm start"
echo "4. Redis: redis-server (или docker run -p 6379:6379 redis:alpine)"
echo ""
echo "Или используйте Docker:"
echo "docker-compose up -d"
