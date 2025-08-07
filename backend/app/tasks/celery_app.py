from celery import Celery
from celery.schedules import crontab
from app.config.settings import settings

# Создание экземпляра Celery
celery_app = Celery(
    "youtube_downloader",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.download_tasks"]
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут максимум на задачу
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
    # Настройка периодических задач
    beat_schedule={
        'cleanup-expired-files-by-time': {
            'task': 'app.tasks.download_tasks.cleanup_expired_files_by_time',
            'schedule': crontab(minute='*/10'),  # Каждые 10 минут
        },
        'cleanup-old-expired-files': {
            'task': 'app.tasks.download_tasks.cleanup_expired_files',
            'schedule': crontab(hour=2, minute=0),  # Каждый день в 2:00
        },
    },
)
