from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.download import DownloadStatus, DownloadFormat

# Схемы для запросов

class DownloadRequest(BaseModel):
    url: HttpUrl = Field(..., description="YouTube URL для загрузки")
    format: DownloadFormat = Field(DownloadFormat.VIDEO_MP4, description="Формат файла")
    quality: Optional[str] = Field("best", description="Качество видео (720p, 1080p, best)")
    audio_only: bool = Field(False, description="Загрузить только аудио")
    
    @validator('url')
    def validate_youtube_url(cls, v):
        url_str = str(v)
        if not any(domain in url_str for domain in ['youtube.com', 'youtu.be']):
            raise ValueError('URL должен быть YouTube ссылкой')
        return v

class VideoInfoRequest(BaseModel):
    url: HttpUrl = Field(..., description="YouTube URL для получения информации")
    
    @validator('url')
    def validate_youtube_url(cls, v):
        url_str = str(v)
        if not any(domain in url_str for domain in ['youtube.com', 'youtu.be']):
            raise ValueError('URL должен быть YouTube ссылкой')
        return v

# Схемы для ответов

class VideoInfo(BaseModel):
    video_id: str
    title: str
    description: Optional[str]
    duration: Optional[int]
    thumbnail: Optional[str]
    channel_name: Optional[str]
    view_count: Optional[int]
    available_formats: List[dict]
    
class DownloadResponse(BaseModel):
    id: str
    status: DownloadStatus
    video_info: Optional[VideoInfo]
    download_url: Optional[str]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class DownloadStatus(BaseModel):
    id: str
    status: DownloadStatus
    progress: Optional[float] = Field(None, description="Прогресс в процентах")
    error_message: Optional[str]
    file_name: Optional[str]
    file_size: Optional[float]
    download_url: Optional[str]
    
    class Config:
        from_attributes = True

class DownloadHistory(BaseModel):
    downloads: List[DownloadResponse]
    total: int
    page: int
    per_page: int
    
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str]
    code: Optional[str]
