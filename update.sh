#!/bin/bash

# Скрипт обновления проекта
set -e

echo "🔄 Обновляем YouTube Downloader..."

# Проверяем, что мы в правильной директории
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Файл docker-compose.prod.yml не найден!"
    echo "Убедитесь, что вы находитесь в корне проекта"
    exit 1
fi

echo "📥 Получаем обновления из Git..."
git fetch origin main
git pull origin main

echo "🛑 Останавливаем текущие сервисы..."
docker-compose -f docker-compose.prod.yml down

echo "🔨 Пересобираем образы..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🚀 Запускаем обновленные сервисы..."
docker-compose -f docker-compose.prod.yml up -d

echo "⏳ Ждем запуска сервисов..."
sleep 30

echo "📊 Проверяем статус..."
docker-compose -f docker-compose.prod.yml ps

echo "🎉 Обновление завершено!"
echo ""
echo "🌐 Сайт: https://ytubik.sarsembai.com"
echo "📋 Логи: docker-compose -f docker-compose.prod.yml logs -f"
