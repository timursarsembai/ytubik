#!/bin/bash
# Тестовый / локальный деплой без влияния на prod .env
# Использует docker-compose.prod.yml, но форсирует DOMAIN=localhost
# Можно быстро поднять окружение и посмотреть работоспособность.

set -euo pipefail

echo "🧪 Тестовый деплой ytubik (локально)"

COMPOSE_FILE="docker-compose.prod.yml"
if [ ! -f "$COMPOSE_FILE" ]; then
  echo "❌ Не найден $COMPOSE_FILE"; exit 1
fi

# Определяем docker compose
if command -v docker &>/dev/null && docker compose version &>/dev/null; then
  DC="docker compose"
elif command -v docker-compose &>/dev/null; then
  DC="docker-compose"
else
  echo "❌ Docker Compose не найден"; exit 1
fi

# Создаем отдельный файл переменных для теста (.env.test) чтобы не трогать prod .env
TEST_ENV_FILE=".env.test"
if [ ! -f "$TEST_ENV_FILE" ]; then
  echo "⚙️ Генерирую $TEST_ENV_FILE"
  cat > "$TEST_ENV_FILE" <<EOF
DOMAIN=localhost
DB_PASSWORD=test_password
SECRET_KEY=$(openssl rand -hex 16)
ENVIRONMENT=testing
DEBUG=true
EOF
fi

echo "✅ Используем переменные из $TEST_ENV_FILE"

export $(grep -v '^#' "$TEST_ENV_FILE" | xargs -I '{}' echo '{}' ) || true

echo "🐳 Строим образы (с кэшем)..."
$DC -f $COMPOSE_FILE build

echo "🚀 Запуск контейнеров (detached)..."
$DC -f $COMPOSE_FILE up -d

echo "⏳ Ждём несколько секунд старта..."
sleep 8

echo "🔍 Сервисы:"
$DC -f $COMPOSE_FILE ps

echo "🩺 Проверка API:"
set +e
curl -s -o /dev/null -w '  /api/docs -> HTTP %{http_code}\n' http://localhost/api/docs
curl -s -o /dev/null -w '  /health (если проксируется) -> HTTP %{http_code}\n' http://localhost/health
set -e

cat <<MSG
✅ Локальный тестовый деплой завершён.

Открыть фронт:   http://localhost
Документация API: http://localhost/api/docs

Полезные команды:
  Логи backend:   $DC -f $COMPOSE_FILE logs -f backend
  Логи celery:    $DC -f $COMPOSE_FILE logs -f celery_worker
  Остановка:      $DC -f $COMPOSE_FILE down
  Очистка с данными: $DC -f $COMPOSE_FILE down -v

Использован отдельный файл переменных: $TEST_ENV_FILE
Prod .env не затронут.
MSG
