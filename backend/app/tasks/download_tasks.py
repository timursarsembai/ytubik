import os
import yt_dlp
import structlog
from celery import current_task
from typing import Dict, Any

from app.tasks.celery_app import celery_app
from app.models.database import SessionLocal
from app.models.download import DownloadStatus
from app.services.download_service import DownloadService
from app.services.youtube_service import YouTubeService
from app.config.settings import settings

logger = structlog.get_logger()

class DownloadProgress:
    """Класс для отслеживания прогресса загрузки"""
    
    def __init__(self, download_id: str):
        self.download_id = download_id
        self.last_progress = 0
    
    def __call__(self, d):
        if d['status'] == 'downloading':
            try:
                # Вычисляем прогресс
                if 'total_bytes' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif 'total_bytes_estimate' in d:
                    progress = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                else:
                    progress = 0
                
                # Обновляем прогресс только если изменился на 5%
                if abs(progress - self.last_progress) >= 5:
                    current_task.update_state(
                        state='PROGRESS',
                        meta={
                            'progress': round(progress, 1),
                            'downloaded': d.get('downloaded_bytes', 0),
                            'total': d.get('total_bytes', d.get('total_bytes_estimate', 0)),
                            'speed': d.get('speed', 0),
                            'eta': d.get('eta', 0)
                        }
                    )
                    self.last_progress = progress
                    
            except Exception as e:
                logger.error("Ошибка обновления прогресса", error=str(e))

@celery_app.task(bind=True)
def download_video_task(self, download_id: str) -> Dict[str, Any]:
    """Асинхронная задача загрузки видео"""
    
    db = SessionLocal()
    download_service = DownloadService(db)
    youtube_service = YouTubeService()
    
    try:
        # Получаем запись загрузки
        download = download_service.get_download(download_id)
        if not download:
            raise ValueError(f"Загрузка {download_id} не найдена")
        
        # Обновляем статус на "обработка"
        download_service.update_download_status(download_id, DownloadStatus.PROCESSING)
        
        # Получаем информацию о видео
        video_info_dict = youtube_service.get_video_info_sync(download.youtube_url)
        download_service.update_video_info(download_id, video_info_dict)
        
        # Настройки для загрузки
        ydl_opts = youtube_service.get_download_options(
            download.format, 
            download.quality, 
            download.audio_only
        )
        
        # Добавляем hook для отслеживания прогресса
        progress_tracker = DownloadProgress(download_id)
        ydl_opts['progress_hooks'] = [progress_tracker]
        
        logger.info("Начинаем загрузку видео", 
                   download_id=download_id,
                   video_title=video_info_dict.get('title', 'Unknown'))
        
        # Пробуем загрузить видео с основными настройками
        download_success = False
        error_message = None
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([download.youtube_url])
            download_success = True
            logger.info("Загрузка успешна с основными настройками", download_id=download_id)
        except Exception as e:
            error_message = str(e)
            logger.warning("Основной метод загрузки не удался, пробуем альтернативный", 
                         download_id=download_id, error=error_message)
            
            # Пробуем альтернативный метод с Android клиентом
            try:
                alternative_opts = youtube_service.get_alternative_download_options(
                    download.format, 
                    download.quality, 
                    download.audio_only
                )
                alternative_opts['progress_hooks'] = [progress_tracker]
                
                with yt_dlp.YoutubeDL(alternative_opts) as ydl:
                    ydl.download([download.youtube_url])
                download_success = True
                logger.info("Загрузка успешна с альтернативными настройками", download_id=download_id)
            except Exception as e2:
                error_message = f"Основной метод: {error_message}. Альтернативный метод: {str(e2)}"
                logger.error("Оба метода загрузки не удались", download_id=download_id, error=error_message)
        
        if not download_success:
            raise ValueError(error_message)
        
        # Находим загруженный файл
        downloaded_files = []
        for file in os.listdir(settings.DOWNLOAD_DIR):
            if download.video_id in file:
                downloaded_files.append(file)
        
        if not downloaded_files:
            raise ValueError("Загруженный файл не найден")
        
        # Берем первый найденный файл
        file_name = downloaded_files[0]
        file_path = os.path.join(settings.DOWNLOAD_DIR, file_name)
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        
        # Проверяем размер файла
        if file_size > settings.MAX_FILE_SIZE_MB:
            os.remove(file_path)
            raise ValueError(f"Файл слишком большой: {file_size:.1f}MB")
        
        # Обновляем информацию о файле
        download_service.update_download_file_info(
            download_id, file_path, file_name, file_size
        )
        
        # Обновляем статус на "завершено"
        download_service.update_download_status(download_id, DownloadStatus.COMPLETED)
        
        logger.info("Загрузка завершена успешно",
                   download_id=download_id,
                   file_name=file_name,
                   file_size=f"{file_size:.1f}MB")
        
        return {
            'status': 'completed',
            'download_id': download_id,
            'file_name': file_name,
            'file_size': file_size,
            'video_title': video_info_dict.get('title', 'Unknown')
        }
        
    except Exception as e:
        error_msg = str(e)
        logger.error("Ошибка загрузки видео",
                    download_id=download_id,
                    error=error_msg)
        
        # Обновляем статус на "ошибка"
        download_service.update_download_status(
            download_id, 
            DownloadStatus.FAILED, 
            error_msg
        )
        
        # Обновляем состояние задачи
        self.update_state(
            state='FAILURE',
            meta={'error': error_msg}
        )
        
        return {
            'status': 'failed',
            'download_id': download_id,
            'error': error_msg
        }
    
    finally:
        db.close()

@celery_app.task
def cleanup_expired_files():
    """Периодическая задача очистки истекших файлов"""
    db = SessionLocal()
    download_service = DownloadService(db)
    
    try:
        cleaned_count = download_service.cleanup_expired_downloads()
        logger.info("Выполнена очистка файлов", cleaned_count=cleaned_count)
        return {'cleaned_files': cleaned_count}
    
    except Exception as e:
        logger.error("Ошибка очистки файлов", error=str(e))
        return {'error': str(e)}
    
    finally:
        db.close()
