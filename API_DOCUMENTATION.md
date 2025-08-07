# API Documentation - YouTube Video Downloader

## 🚀 Обзор

YouTube Video Downloader предоставляет REST API для скачивания видео с YouTube, включая поддержку YouTube Shorts. API использует сессионную аутентификацию через HTTP cookies для изоляции пользователей.

**Base URL:** `http://localhost:8000/api`

## 🔐 Аутентификация

API использует сессионную аутентификацию через HTTP cookies:

```http
Cookie: session_id=your_session_id
```

Сессия создается автоматически при первом запросе. Backend генерирует уникальный `session_id` на основе IP адреса, User-Agent и UUID.

## 📊 Поддерживаемые URL форматы

```bash
# Обычные YouTube видео
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ

# YouTube Shorts
https://www.youtube.com/shorts/iak2v82mS0A
```

## 📡 Endpoints

### 1. Создание загрузки

**POST** `/download`

Создает новую задачу загрузки видео.

#### Request Body

```json
{
  "url": "string",           // YouTube URL (обязательно)
  "format": "string",        // Формат файла (по умолчанию: "video_mp4")
  "quality": "string",       // Качество (по умолчанию: "best")
  "audio_only": boolean      // Только аудио (по умолчанию: false)
}
```

#### Supported Formats

- `video_mp4` - MP4 видео
- `video_webm` - WebM видео
- `audio_mp3` - MP3 аудио
- `audio_aac` - AAC аудио

#### Supported Quality

- `best` - Лучшее доступное качество
- `720p` - 720p
- `1080p` - 1080p
- `480p` - 480p

#### Response

```json
{
  "id": "string",                    // ID загрузки
  "status": "pending",               // Статус загрузки
  "video_info": {
    "video_id": "string",
    "title": "string",
    "description": "string",
    "duration": 48,
    "thumbnail": "string",
    "channel_name": "string",
    "view_count": 1000000,
    "available_formats": [...]
  },
  "download_url": null,              // URL файла (после завершения)
  "error_message": null,
  "created_at": "2025-08-07T21:41:19"
}
```

#### Example

```bash
curl -X POST "http://localhost:8000/api/download" \
  -H "Content-Type: application/json" \
  -H "Cookie: session_id=your_session" \
  -d '{
    "url": "https://www.youtube.com/shorts/iak2v82mS0A",
    "format": "video_mp4",
    "quality": "best",
    "audio_only": false
  }'
```

### 2. Проверка статуса загрузки

**GET** `/download/{id}/status`

Получает текущий статус загрузки.

#### Response

```json
{
  "id": "string",
  "status": "completed", // pending, processing, completed, failed, expired
  "progress": 100, // Прогресс в процентах
  "error_message": null,
  "download_url": "/api/download/id/file",
  "file_size": 3.42, // Размер в MB
  "created_at": "2025-08-07T21:41:19"
}
```

#### Status Values

- `pending` - В очереди на обработку
- `processing` - Обрабатывается
- `completed` - Завершено успешно
- `failed` - Ошибка
- `expired` - Истек срок файла

### 3. Скачивание файла

**GET** `/download/{id}/file`

Скачивает готовый файл.

#### Response

- **200 OK** - Файл передается с правильными заголовками
- **404 Not Found** - Файл не найден или истек срок
- **400 Bad Request** - Загрузка не завершена

#### Headers

```http
Content-Type: video/mp4; audio/mpeg
Content-Disposition: attachment; filename="video_title.mp4"
Content-Length: file_size_bytes
```

### 4. История загрузок пользователя

**GET** `/downloads/my`

Получает список загрузок текущего пользователя (сессии).

#### Query Parameters

- `page` (int, по умолчанию: 1) - Номер страницы
- `per_page` (int, по умолчанию: 20) - Элементов на странице

#### Response

```json
{
  "downloads": [
    {
      "id": "string",
      "status": "completed",
      "video_info": {
        "video_id": "string",
        "title": "string",
        "duration": 48,
        "thumbnail": "string",
        "channel_name": "string"
      },
      "download_url": "/api/download/id/file",
      "created_at": "2025-08-07T21:41:19"
    }
  ],
  "total": 10,
  "page": 1,
  "per_page": 20
}
```

### 5. Глобальная активность

**GET** `/downloads/global`

Получает глобальную активность всех пользователей (только названия видео и даты).

#### Query Parameters

- `page` (int, по умолчанию: 1) - Номер страницы
- `per_page` (int, по умолчанию: 10) - Элементов на странице

#### Response

```json
{
  "activity": [
    {
      "video_title": "Tucker Unleashed‼️ 🔥🔥",
      "created_at": "2025-08-07T21:41:19"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 10
}
```

### 6. Очистка файлов пользователя

**DELETE** `/downloads/cleanup-user`

Удаляет все файлы текущего пользователя.

#### Response

```json
{
  "message": "User files cleaned up successfully",
  "cleaned_count": 5
}
```

### 7. Получение информации о видео

**POST** `/video/info`

Получает информацию о видео без скачивания.

#### Request Body

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

#### Response

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "description": "...",
  "duration": 213,
  "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "channel_name": "Rick Astley",
  "view_count": 1500000000,
  "available_formats": [...]
}
```

### 8. Проверка здоровья сервиса

**GET** `/health`

Проверяет состояние сервиса.

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2025-08-07T21:41:19",
  "services": {
    "database": "ok",
    "redis": "ok",
    "celery": "ok"
  }
}
```

## ⚠️ Коды ошибок

### HTTP Status Codes

- **200 OK** - Успешный запрос
- **201 Created** - Ресурс создан (новая загрузка)
- **400 Bad Request** - Неверные параметры запроса
- **404 Not Found** - Ресурс не найден
- **422 Unprocessable Entity** - Ошибка валидации
- **429 Too Many Requests** - Превышен лимит запросов
- **500 Internal Server Error** - Внутренняя ошибка сервера

### Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2025-08-07T21:41:19"
}
```

### Common Error Codes

- `INVALID_URL` - Неверный YouTube URL
- `VIDEO_TOO_LONG` - Видео слишком длинное
- `VIDEO_NOT_AVAILABLE` - Видео недоступно
- `RATE_LIMIT_EXCEEDED` - Превышен лимит запросов
- `SESSION_REQUIRED` - Требуется сессия

## 🔄 Rate Limiting

### Лимиты по умолчанию:

- **50 загрузок в час** на сессию
- **200 загрузок в день** на сессию

### Headers ответа:

```http
X-RateLimit-Limit: 50
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1659888000
```

## 📁 Жизненный цикл файлов

1. **Создание** - Файл создается после успешной загрузки
2. **Доступность** - Файл доступен в течение 1 часа
3. **Истечение** - Статус меняется на `expired`
4. **Удаление** - Файл и запись удаляются через 1 минуту после истечения

## 🔧 Интеграция

### Python Example

```python
import requests

class YouTubeDownloader:
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        self.session = requests.Session()

    def download_video(self, url, format="video_mp4", quality="best"):
        response = self.session.post(f"{self.base_url}/download", json={
            "url": url,
            "format": format,
            "quality": quality,
            "audio_only": False
        })
        return response.json()

    def get_status(self, download_id):
        response = self.session.get(f"{self.base_url}/download/{download_id}/status")
        return response.json()

    def download_file(self, download_id, output_path):
        response = self.session.get(f"{self.base_url}/download/{download_id}/file")
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        return False

# Использование
downloader = YouTubeDownloader()

# Скачивание YouTube Shorts
result = downloader.download_video("https://www.youtube.com/shorts/iak2v82mS0A")
download_id = result["id"]

# Проверка статуса
status = downloader.get_status(download_id)
if status["status"] == "completed":
    downloader.download_file(download_id, "video.mp4")
```

### JavaScript Example

```javascript
class YouTubeDownloaderAPI {
  constructor(baseUrl = "http://localhost:8000/api") {
    this.baseUrl = baseUrl;
  }

  async downloadVideo(url, format = "video_mp4", quality = "best") {
    const response = await fetch(`${this.baseUrl}/download`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include", // Важно для cookies
      body: JSON.stringify({
        url,
        format,
        quality,
        audio_only: false,
      }),
    });
    return response.json();
  }

  async getMyDownloads(page = 1, perPage = 20) {
    const response = await fetch(
      `${this.baseUrl}/downloads/my?page=${page}&per_page=${perPage}`,
      { credentials: "include" }
    );
    return response.json();
  }

  async getGlobalActivity(page = 1, perPage = 10) {
    const response = await fetch(
      `${this.baseUrl}/downloads/global?page=${page}&per_page=${perPage}`
    );
    return response.json();
  }
}

// Использование
const api = new YouTubeDownloaderAPI();

// Скачивание видео
const result = await api.downloadVideo(
  "https://www.youtube.com/shorts/iak2v82mS0A"
);
console.log("Download started:", result.id);

// Получение моих загрузок
const myDownloads = await api.getMyDownloads();
console.log("My downloads:", myDownloads.downloads);
```

## 📋 Changelog API

### v3.0.0

- ✅ Добавлена поддержка YouTube Shorts
- ✅ Сессионная аутентификация через cookies
- ✅ Новые endpoints: `/downloads/my`, `/downloads/global`, `/downloads/cleanup-user`
- ✅ Автоматическое удаление файлов через 1 час
- ✅ Улучшенная система безопасности

### v2.0.0

- ✅ Обновлен yt-dlp до 2025.7.21
- ✅ Улучшена обработка ошибок YouTube
- ✅ Добавлен rate limiting

### v1.0.0

- ✅ Базовый функционал загрузки видео
- ✅ REST API endpoints
- ✅ Celery интеграция

---

Для получения актуальной документации API в интерактивном виде посетите:
**http://localhost:8000/docs** (Swagger UI)
