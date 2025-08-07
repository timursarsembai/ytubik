#!/bin/bash

# Скрипт для запуска YouTube downloader в режиме разработки
# Требует установленного Docker, Node.js и Python

echo "🚀 Запуск YouTube Downloader MVP..."

# Проверяем зависимости
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Пожалуйста, установите Docker."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js не установлен. Пожалуйста, установите Node.js."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен. Пожалуйста, установите Python3."
    exit 1
fi

# Переходим в директорию проекта
cd "$(dirname "$0")"

echo "📦 Запуск сервисов Docker (Redis, PostgreSQL)..."
docker-compose up -d redis postgres

# Ждем, пока поднимутся сервисы
echo "⏳ Ожидание готовности сервисов..."
sleep 10

echo "🐍 Запуск Backend (FastAPI)..."
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

echo "⚛️ Запуск Frontend (React)..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "👷 Запуск Celery Worker..."
cd backend
source venv/bin/activate
celery -A app.tasks.download_tasks worker --loglevel=info &
CELERY_PID=$!
cd ..

echo ""
echo "✅ Все сервисы запущены!"
echo ""
echo "🌐 Доступные URL:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Для остановки всех сервисов нажмите Ctrl+C"

# Функция для завершения всех процессов
cleanup() {
    echo ""
    echo "🛑 Остановка сервисов..."
    kill $BACKEND_PID $FRONTEND_PID $CELERY_PID 2>/dev/null
    docker-compose down
    echo "✅ Все сервисы остановлены."
    exit 0
}

# Ловим сигнал прерывания
trap cleanup SIGINT SIGTERM

# Ждем завершения
wait
