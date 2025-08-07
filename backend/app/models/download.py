from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.models.database import Base

class DownloadStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"

class DownloadFormat(str, enum.Enum):
    VIDEO_MP4 = "video_mp4"
    VIDEO_WEBM = "video_webm"
    AUDIO_MP3 = "audio_mp3"
    AUDIO_AAC = "audio_aac"

class Download(Base):
    __tablename__ = "downloads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # URL и метаданные видео
    youtube_url = Column(String, nullable=False)
    video_id = Column(String, nullable=False)  # YouTube video ID
    video_title = Column(String, nullable=True)
    video_description = Column(Text, nullable=True)
    video_duration = Column(Integer, nullable=True)  # в секундах
    video_thumbnail = Column(String, nullable=True)
    channel_name = Column(String, nullable=True)
    view_count = Column(Integer, nullable=True)
    
    # Параметры загрузки
    format = Column(String, nullable=False)  # DownloadFormat
    quality = Column(String, nullable=True)  # 720p, 1080p, best, etc.
    audio_only = Column(Boolean, default=False)
    
    # Статус и файлы
    status = Column(String, nullable=False, default=DownloadStatus.PENDING)
    error_message = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    file_size = Column(Float, nullable=True)  # в MB
    
    # IP адрес для rate limiting и session для разделения пользователей
    client_ip = Column(String, nullable=True)
    session_id = Column(String, nullable=True)  # Уникальный идентификатор сессии пользователя
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<Download(id={self.id}, title={self.video_title}, status={self.status})>"
