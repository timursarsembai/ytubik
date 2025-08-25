#!/bin/bash
# Скрипт production деплоя ytubik

set -e

echo "🚀 Начинаем развертывание ytubik..."

# Проверяем, что мы в правильной директории
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Файл docker-compose.prod.yml не найден!"
    echo "Убедитесь, что вы находитесь в корне проекта"
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo "⚙️ Создаем .env (не найден)"
    cat > .env <<EOF
DOMAIN=ytubik.sarsembai.com
DB_PASSWORD=$(openssl rand -hex 12)
SECRET_KEY=$(openssl rand -hex 32)
EOF
    echo "✅ Сгенерирован .env"
fi

# Проверяем наличие обязательных переменных
source .env
missing=()
[ -z "$DOMAIN" ] && missing+=(DOMAIN)
[ -z "$DB_PASSWORD" ] && missing+=(DB_PASSWORD)
[ -z "$SECRET_KEY" ] && missing+=(SECRET_KEY)
if [ ${#missing[@]} -gt 0 ]; then
    echo "❌ Отсутствуют переменные: ${missing[*]}"; exit 1; fi

# Определяем бинарь docker compose
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
    DC="docker compose"
elif command -v docker-compose &>/dev/null; then
    DC="docker-compose"
else
    echo "❌ Docker Compose не найден"; exit 1
fi

echo "✅ Останавливаем старые контейнеры..."
$DC -f docker-compose.prod.yml down || true

echo "✅ Собираем/обновляем образы..."
$DC -f docker-compose.prod.yml build

echo "✅ Запускаем сервисы..."
$DC -f docker-compose.prod.yml up -d --remove-orphans

echo "✅ Ждем запуска сервисов..."
sleep 30

echo "✅ Проверяем статус сервисов..."
$DC -f docker-compose.prod.yml ps

echo "ℹ️ Пропускаем явное создание таблиц (создаются при старте FastAPI)"

echo "🎉 Развертывание завершено!"
echo ""
echo "📊 Проверить статус: docker-compose -f docker-compose.prod.yml ps"
echo "📋 Посмотреть логи: docker-compose -f docker-compose.prod.yml logs -f"
echo "🌐 Сайт (HTTP) должен быть доступен: http://$DOMAIN"
echo ""
echo "🔧 Полезные команды:"
echo "- Перезапуск: $DC -f docker-compose.prod.yml restart"
echo "- Остановка: $DC -f docker-compose.prod.yml down"
echo "- Обновление: git pull && ./deploy.sh"
