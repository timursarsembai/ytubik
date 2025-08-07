# YouTube Video Downloader MVP

Автономный веб-сервис для скачивания видео с YouTube с возможностью интеграции с Telegram-ботом.

## 🚀 Особенности

- 🎥 Скачивание видео с YouTube в различных форматах и качествах
- 🎵 Извлечение только аудио в MP3
- ⚡ Асинхронная обработка загрузок через Celery
- 📊 История загрузок с пагинацией
- 🔒 Rate limiting и безопасность
- 📱 Responsive веб-интерфейс на React + Material-UI
- 🤖 REST API для интеграции с Telegram-ботом
- 🐳 Docker поддержка для легкого деплоя

## 🛠 Технологии

**Backend:**

- Python 3.13+ с FastAPI
- yt-dlp 2025.7.21 для загрузки видео (с поддержкой обхода блокировок YouTube)
- SQLAlchemy + PostgreSQL/SQLite
- Redis + Celery для асинхронных задач
- Pydantic для валидации
- Structlog для логирования

**Frontend:**

- React.js + TypeScript
- Material-UI компоненты
- React Query для state management
- Axios для HTTP запросов

**Инфраструктура:**

- Docker + Docker Compose
- Nginx reverse proxy
- Redis для кэширования и очередей

## 📁 Структура проекта

```
youtube-downloader/
├── backend/                # FastAPI приложение
│   ├── app/
│   │   ├── controllers/    # API endpoints
│   │   ├── models/        # Database models
│   │   ├── services/      # Business logic
│   │   ├── tasks/         # Celery tasks
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── config/        # Configuration
│   │   └── utils/         # Helpers
│   ├── tests/             # Тесты
│   └── requirements.txt   # Python зависимости
├── frontend/              # React приложение
│   ├── src/
│   │   ├── components/    # React компоненты
│   │   └── services/      # API клиент
│   └── package.json       # Node.js зависимости
├── docker-compose.yml     # Docker конфигурация
├── Makefile              # Команды разработки
└── README.md             # Документация
```

## 🚀 Быстрый старт

### Через Docker (рекомендуется)

1. **Клонирование репозитория:**

```bash
git clone <repository-url>
cd youtube-downloader
```

2. **Запуск в development режиме:**

```bash
make docker-dev
```

3. **Доступ к приложению:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

### Локальная разработка

1. **Установка зависимостей:**

```bash
make install
# или
./setup_dev.sh
```

2. **Запуск Redis:**

```bash
make redis
# или
redis-server
```

3. **Запуск сервисов (в отдельных терминалах):**

```bash
# Backend
make backend

# Celery Worker
make worker

# Frontend
make frontend
```

## 🐳 Production деплой

1. **Подготовка сервера:**

```bash
# Установка Docker и Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

2. **Деплой:**

```bash
./deploy_prod.sh
# или
make docker-prod
```

3. **Настройка домена:**

- Настройте DNS для saveforme.sarsembai.com
- Обновите nginx.conf для SSL
- Настройте SSL сертификаты

## 📡 API Endpoints

### Основные endpoints:

- `POST /api/download` - Создание новой загрузки
- `GET /api/download/{id}/status` - Статус загрузки
- `GET /api/download/{id}/file` - Скачивание файла
- `GET /api/downloads` - История загрузок
- `POST /api/video/info` - Информация о видео

### Пример использования:

```bash
# Создание загрузки
curl -X POST "http://localhost:8000/api/download" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "format": "video_mp4",
    "quality": "720p",
    "audio_only": false
  }'

# Проверка статуса
curl "http://localhost:8000/api/download/{id}/status"
```

## ⚙️ Конфигурация

Основные настройки в `backend/.env`:

```env
# Ограничения
MAX_FILE_SIZE_MB=500
FILE_RETENTION_HOURS=24
RATE_LIMIT_DOWNLOADS_PER_HOUR=50
RATE_LIMIT_DOWNLOADS_PER_DAY=200

# YouTube настройки
MAX_VIDEO_DURATION_MINUTES=60
ALLOWED_VIDEO_FORMATS=mp4,webm,mkv
ALLOWED_AUDIO_FORMATS=mp3,aac,wav
```

## 🔒 Безопасность

- Rate limiting по IP адресам
- Валидация всех входных данных
- Автоудаление файлов через 24 часа
- Ограничение размера и длительности видео
- CORS настройки для безопасности

## 🆕 Последние обновления

**v2.0.0 (Август 2025)**

- ✅ Обновлен yt-dlp до версии 2025.7.21 с улучшенной поддержкой YouTube
- ✅ Реализован обход блокировок YouTube через web client и Android client
- ✅ Добавлена двойная система загрузки (основная + резервная)
- ✅ Исправлены ошибки отображения rate limiting в React интерфейсе
- ✅ Улучшена обработка ошибок HTTP 403 Forbidden
- ✅ Добавлены анти-детект заголовки для YouTube

## 🧪 Тестирование

```bash
# Запуск тестов
make test

# Или раздельно
cd backend && pytest
cd frontend && npm test
```

## 📊 Мониторинг

- Структурированное логирование через structlog
- Celery мониторинг задач
- Docker контейнеры health checks

## 🤖 Интеграция с Telegram

API готов для интеграции с Telegram-ботом:

```python
import requests

# Создание загрузки
response = requests.post('http://your-domain/api/download', json={
    'url': youtube_url,
    'format': 'video_mp4',
    'quality': 'best',
    'audio_only': False
})

download_id = response.json()['id']

# Проверка статуса
status = requests.get(f'http://your-domain/api/download/{download_id}/status')
```

## 🛠 Команды разработки

```bash
make help          # Список всех команд
make install       # Установка зависимостей
make docker-dev    # Запуск через Docker
make test          # Запуск тестов
make clean         # Очистка временных файлов
make logs          # Просмотр логов
make stop          # Остановка сервисов
```

## 📈 Планы развития

- [ ] Поддержка других платформ (Instagram, TikTok)
- [ ] Telegram-бот интеграция
- [ ] Плейлисты и пакетная загрузка
- [ ] Планировщик загрузок
- [ ] Система уведомлений
- [ ] Аналитика и статистика

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Сделайте изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License - см. LICENSE файл

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `make logs`
2. Посмотрите статус: `make status`
3. Создайте issue в репозитории

---

**Примечание:** Этот проект предназначен только для личного использования. Соблюдайте авторские права и условия использования YouTube.
