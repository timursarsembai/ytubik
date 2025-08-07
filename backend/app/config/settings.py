from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Основные настройки
    APP_NAME: str = "YouTube Video Downloader"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # База данных
    DATABASE_URL: str = "sqlite:///./youtube_downloader.db"
    
    # Redis и Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Файловая система
    DOWNLOAD_DIR: str = os.path.abspath("../downloads")
    MAX_FILE_SIZE_MB: int = 500
    FILE_RETENTION_HOURS: int = 24
    USER_FILE_RETENTION_HOURS: int = 1  # Время жизни пользовательских файлов
    
    # Rate limiting
    RATE_LIMIT_DOWNLOADS_PER_HOUR: int = 50
    RATE_LIMIT_DOWNLOADS_PER_DAY: int = 200
    
    # YouTube настройки
    YOUTUBE_DL_FORMAT: str = "best[height<=1080]"
    ALLOWED_VIDEO_FORMATS: List[str] = ["mp4", "webm", "mkv"]
    ALLOWED_AUDIO_FORMATS: List[str] = ["mp3", "aac", "wav"]
    MAX_VIDEO_DURATION_MINUTES: int = 60
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "https://saveforme.sarsembai.com"
    ]
    
    # Безопасность
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Создание экземпляра настроек
settings = Settings()

# Создание директории для загрузок
os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)
