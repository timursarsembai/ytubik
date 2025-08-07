from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime, timedelta
import structlog
import os

from app.models.download import Download, DownloadStatus
from app.models.database import get_db
from app.config.settings import settings

logger = structlog.get_logger()

class DownloadService:
    """Сервис для управления загрузками"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_download(self, 
                       youtube_url: str,
                       video_id: str,
                       format_type: str,
                       quality: str,
                       audio_only: bool,
                       client_ip: str,
                       session_id: str) -> Download:
        """Создает новую запись загрузки"""
        
        download = Download(
            youtube_url=youtube_url,
            video_id=video_id,
            format=format_type,
            quality=quality,
            audio_only=audio_only,
            client_ip=client_ip,
            session_id=session_id,
            status=DownloadStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(hours=settings.FILE_RETENTION_HOURS)
        )
        
        self.db.add(download)
        self.db.commit()
        self.db.refresh(download)
        
        logger.info("Создана новая загрузка", 
                   download_id=download.id,
                   video_id=video_id,
                   client_ip=client_ip,
                   session_id=session_id)
        
        return download
    
    def get_download(self, download_id: str) -> Optional[Download]:
        """Получает загрузку по ID"""
        return self.db.query(Download).filter(Download.id == download_id).first()
    
    def update_download_status(self, 
                              download_id: str, 
                              status: DownloadStatus,
                              error_message: str = None) -> Optional[Download]:
        """Обновляет статус загрузки"""
        download = self.get_download(download_id)
        if not download:
            return None
        
        download.status = status
        if error_message:
            download.error_message = error_message
        
        if status == DownloadStatus.PROCESSING:
            download.started_at = datetime.utcnow()
        elif status == DownloadStatus.COMPLETED:
            download.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(download)
        
        logger.info("Обновлен статус загрузки",
                   download_id=download_id,
                   status=status,
                   error=error_message)
        
        return download
    
    def update_download_file_info(self, 
                                 download_id: str,
                                 file_path: str,
                                 file_name: str,
                                 file_size: float) -> Optional[Download]:
        """Обновляет информацию о файле"""
        download = self.get_download(download_id)
        if not download:
            return None
        
        download.file_path = file_path
        download.file_name = file_name
        download.file_size = file_size
        
        self.db.commit()
        self.db.refresh(download)
        
        logger.info("Обновлена информация о файле",
                   download_id=download_id,
                   file_name=file_name,
                   file_size=file_size)
        
        return download
    
    def update_video_info(self, download_id: str, video_info: dict) -> Optional[Download]:
        """Обновляет информацию о видео"""
        download = self.get_download(download_id)
        if not download:
            return None
        
        download.video_title = video_info.get('title')
        download.video_description = video_info.get('description')
        download.video_duration = video_info.get('duration')
        download.video_thumbnail = video_info.get('thumbnail')
        download.channel_name = video_info.get('channel_name')
        download.view_count = video_info.get('view_count')
        
        self.db.commit()
        self.db.refresh(download)
        
        return download
    
    def get_downloads_by_ip(self, client_ip: str, hours: int = 1) -> List[Download]:
        """Получает загрузки по IP за определенный период"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        return self.db.query(Download).filter(
            and_(
                Download.client_ip == client_ip,
                Download.created_at >= time_threshold
            )
        ).all()
    
    def get_downloads_history(self, 
                            page: int = 1, 
                            per_page: int = 20,
                            client_ip: str = None) -> tuple[List[Download], int]:
        """Получает историю загрузок с пагинацией"""
        query = self.db.query(Download)
        
        if client_ip:
            query = query.filter(Download.client_ip == client_ip)
        
        total = query.count()
        
        downloads = query.order_by(desc(Download.created_at))\
                        .offset((page - 1) * per_page)\
                        .limit(per_page)\
                        .all()
        
        return downloads, total
    
    def check_rate_limit(self, client_ip: str) -> dict:
        """Проверяет rate limiting для IP"""
        # Проверка за час
        hourly_downloads = self.get_downloads_by_ip(client_ip, hours=1)
        # Проверка за день
        daily_downloads = self.get_downloads_by_ip(client_ip, hours=24)
        
        hourly_count = len(hourly_downloads)
        daily_count = len(daily_downloads)
        
        return {
            'allowed': (hourly_count < settings.RATE_LIMIT_DOWNLOADS_PER_HOUR and 
                       daily_count < settings.RATE_LIMIT_DOWNLOADS_PER_DAY),
            'hourly_count': hourly_count,
            'hourly_limit': settings.RATE_LIMIT_DOWNLOADS_PER_HOUR,
            'daily_count': daily_count,
            'daily_limit': settings.RATE_LIMIT_DOWNLOADS_PER_DAY
        }
    
    def get_global_activity(self, 
                           page: int = 1, 
                           per_page: int = 20) -> tuple[List[Download], int]:
        """Получает глобальную активность всех пользователей"""
        query = self.db.query(Download)
        
        total = query.count()
        
        downloads = query.order_by(desc(Download.created_at))\
                        .offset((page - 1) * per_page)\
                        .limit(per_page)\
                        .all()
        
        return downloads, total
    
    def get_user_downloads(self, 
                          session_id: str,
                          page: int = 1, 
                          per_page: int = 20) -> tuple[List[Download], int]:
        """Получает загрузки конкретного пользователя по session_id"""
        query = self.db.query(Download).filter(Download.session_id == session_id)
        
        total = query.count()
        
        downloads = query.order_by(desc(Download.created_at))\
                        .offset((page - 1) * per_page)\
                        .limit(per_page)\
                        .all()
        
        return downloads, total

    def cleanup_user_downloads(self, session_id: str) -> int:
        """Удаляет все загрузки конкретного пользователя по session_id"""
        user_downloads = self.db.query(Download).filter(
            Download.session_id == session_id
        ).all()
        
        count = 0
        for download in user_downloads:
            # Удаляем файл если существует
            if download.file_path and os.path.exists(download.file_path):
                try:
                    os.remove(download.file_path)
                    logger.info("Удален пользовательский файл", 
                               file_path=download.file_path, 
                               session_id=session_id)
                except Exception as e:
                    logger.error("Ошибка удаления пользовательского файла", 
                                file_path=download.file_path, 
                                session_id=session_id,
                                error=str(e))
            
            # Обновляем статус
            download.status = DownloadStatus.EXPIRED
            count += 1
        
        self.db.commit()
        
        if count > 0:
            logger.info("Очищены пользовательские загрузки", 
                       count=count, 
                       session_id=session_id)
        
        return count

    def cleanup_downloads_by_time(self, hours: int = 1) -> int:
        """Удаляет загрузки старше указанного времени"""
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        expired_downloads = self.db.query(Download).filter(
            and_(
                Download.created_at < time_threshold,
                Download.status == DownloadStatus.COMPLETED
            )
        ).all()
        
        count = 0
        for download in expired_downloads:
            # Удаляем файл если существует
            if download.file_path and os.path.exists(download.file_path):
                try:
                    os.remove(download.file_path)
                    logger.info("Удален файл по времени", 
                               file_path=download.file_path,
                               age_hours=hours)
                except Exception as e:
                    logger.error("Ошибка удаления файла по времени", 
                                file_path=download.file_path, 
                                error=str(e))
            
            # Обновляем статус
            download.status = DownloadStatus.EXPIRED
            count += 1
        
        self.db.commit()
        
        if count > 0:
            logger.info("Очищены загрузки по времени", 
                       count=count, 
                       hours=hours)
        
        return count

    def cleanup_expired_downloads(self) -> int:
        """Удаляет истекшие загрузки"""
        expired_downloads = self.db.query(Download).filter(
            Download.expires_at < datetime.utcnow()
        ).all()
        
        count = 0
        for download in expired_downloads:
            # Удаляем файл если существует
            if download.file_path and os.path.exists(download.file_path):
                try:
                    os.remove(download.file_path)
                    logger.info("Удален файл", file_path=download.file_path)
                except Exception as e:
                    logger.error("Ошибка удаления файла", file_path=download.file_path, error=str(e))
            
            # Обновляем статус
            download.status = DownloadStatus.EXPIRED
            count += 1
        
        self.db.commit()
        
        if count > 0:
            logger.info("Очищены истекшие загрузки", count=count)
        
        return count

    def delete_expired_records(self, minutes_threshold: int = 1) -> int:
        """Удаляет записи со статусом EXPIRED, которые находятся в этом статусе дольше указанного времени"""
        from datetime import datetime, timedelta
        
        threshold_time = datetime.utcnow() - timedelta(minutes=minutes_threshold)
        
        expired_records = self.db.query(Download).filter(
            Download.status == DownloadStatus.EXPIRED,
            Download.updated_at < threshold_time
        ).all()
        
        count = 0
        for download in expired_records:
            # Окончательно удаляем файл если ещё существует
            if download.file_path and os.path.exists(download.file_path):
                try:
                    os.remove(download.file_path)
                    logger.info("Удален файл при удалении записи", file_path=download.file_path)
                except Exception as e:
                    logger.error("Ошибка удаления файла при удалении записи", file_path=download.file_path, error=str(e))
            
            # Удаляем запись из базы данных
            self.db.delete(download)
            count += 1
        
        self.db.commit()
        
        if count > 0:
            logger.info("Удалены записи со статусом EXPIRED", count=count, minutes_threshold=minutes_threshold)
        
        return count
