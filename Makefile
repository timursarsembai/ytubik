.PHONY: help dev prod test clean install

help:
	@echo "YouTube Video Downloader - Команды разработки"
	@echo ""
	@echo "Доступные команды:"
	@echo "  install    - Установка зависимостей для разработки"
	@echo "  dev        - Запуск в режиме разработки"
	@echo "  prod       - Запуск в production режиме"
	@echo "  test       - Запуск тестов"
	@echo "  clean      - Очистка временных файлов"
	@echo "  docker-dev - Запуск через Docker Compose"
	@echo "  docker-prod- Запуск в production через Docker"

install:
	@echo "📦 Установка зависимостей..."
	cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install
	@echo "✅ Зависимости установлены!"

dev:
	@echo "🚀 Запуск в режиме разработки..."
	@echo "Запустите в отдельных терминалах:"
	@echo "1. make backend"
	@echo "2. make worker" 
	@echo "3. make frontend"
	@echo "4. make redis"

backend:
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	cd backend && source venv/bin/activate && celery -A app.tasks.celery_app worker --loglevel=info

frontend:
	cd frontend && npm start

redis:
	redis-server --port 6379

test:
	@echo "🧪 Запуск тестов..."
	cd backend && source venv/bin/activate && pytest
	cd frontend && npm test

docker-dev:
	@echo "🐳 Запуск через Docker Compose (development)..."
	docker-compose up -d
	@echo "✅ Сервисы запущены!"
	@echo "🌐 Frontend: http://localhost:3000"
	@echo "🔗 Backend: http://localhost:8000"
	@echo "📚 API Docs: http://localhost:8000/api/docs"

docker-prod:
	@echo "🐳 Запуск в production через Docker..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
	@echo "✅ Production сервисы запущены!"
	@echo "🌐 Приложение: http://localhost"

stop:
	docker-compose down

logs:
	docker-compose logs -f

clean:
	@echo "🧹 Очистка временных файлов..."
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf backend/downloads/*
	rm -rf frontend/node_modules/.cache
	rm -rf frontend/build
	docker system prune -f
	@echo "✅ Очистка завершена!"

status:
	@echo "📊 Статус сервисов:"
	docker-compose ps
