# Скрипт для развертывания на сервере
#!/bin/bash

set -e

echo "🚀 Начинаем развертывание YouTube Downloader..."

# Проверяем, что мы в правильной директории
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Файл docker-compose.prod.yml не найден!"
    echo "Убедитесь, что вы находитесь в корне проекта"
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "❌ Файл .env не найден!"
    echo "Скопируйте .env.example в .env и настройте переменные:"
    echo "cp .env.example .env"
    echo "nano .env"
    exit 1
fi

echo "✅ Останавливаем старые контейнеры..."
docker-compose -f docker-compose.prod.yml down

echo "✅ Собираем новые образы..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "✅ Запускаем сервисы..."
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Ждем запуска сервисов..."
sleep 30

echo "✅ Проверяем статус сервисов..."
docker-compose -f docker-compose.prod.yml ps

echo "✅ Создаем таблицы в базе данных..."
docker-compose -f docker-compose.prod.yml exec backend python -c "
from database import engine, Base
Base.metadata.create_all(bind=engine)
print('Database tables created successfully!')
"

echo "🎉 Развертывание завершено!"
echo ""
echo "📊 Проверить статус: docker-compose -f docker-compose.prod.yml ps"
echo "📋 Посмотреть логи: docker-compose -f docker-compose.prod.yml logs -f"
echo "🌐 Сайт доступен по адресу: http://ytubik.sarsembai.com"
echo ""
echo "🔧 Полезные команды:"
echo "- Перезапуск: docker-compose -f docker-compose.prod.yml restart"
echo "- Остановка: docker-compose -f docker-compose.prod.yml down"
echo "- Обновление: git pull && ./deploy.sh"
