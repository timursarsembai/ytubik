from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import structlog

from app.config.settings import settings
from app.controllers import download_controller, video_controller
from app.models.database import engine, Base

# Настройка логирования
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="YouTube Video Downloader",
    description="MVP сервис для скачивания видео с YouTube",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(download_controller.router, prefix="/api", tags=["downloads"])
app.include_router(video_controller.router, prefix="/api", tags=["video"])

# Статические файлы для загруженных видео
app.mount("/downloads", StaticFiles(directory=settings.DOWNLOAD_DIR), name="downloads")

@app.on_event("startup")
async def startup_event():
    logger.info("YouTube Downloader API запущен", 
                environment=settings.ENVIRONMENT,
                download_dir=settings.DOWNLOAD_DIR)

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("YouTube Downloader API остановлен")

@app.get("/")
async def root():
    return {
        "message": "YouTube Video Downloader API", 
        "version": "1.0.0",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "youtube-downloader"}
