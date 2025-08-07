#!/bin/bash

# YouTube Video Downloader - Production Deployment

echo "🚀 Деплой YouTube Video Downloader в продакшн..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker сначала."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose сначала."
    exit 1
fi

# Создание production .env файла
if [ ! -f backend/.env ]; then
    echo "⚙️ Создание production .env файла..."
    cat > backend/.env << EOF
# Production настройки
APP_NAME=YouTube Video Downloader
ENVIRONMENT=production
DEBUG=false

# База данных
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/youtube_downloader

# Redis и Celery
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Файловая система
DOWNLOAD_DIR=/app/downloads
MAX_FILE_SIZE_MB=500
FILE_RETENTION_HOURS=24

# Rate limiting
RATE_LIMIT_DOWNLOADS_PER_HOUR=10
RATE_LIMIT_DOWNLOADS_PER_DAY=50

# Безопасность
SECRET_KEY=$(openssl rand -hex 32)
EOF
fi

# Запуск в production режиме
echo "🐳 Запуск контейнеров..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка состояния
echo "🔍 Проверка состояния сервисов..."
docker-compose ps

echo "✅ Деплой завершен!"
echo ""
echo "🌐 Приложение доступно по адресу: http://localhost"
echo "📚 API документация: http://localhost/api/docs"
echo ""
echo "Для остановки: docker-compose down"
echo "Для просмотра логов: docker-compose logs -f"
