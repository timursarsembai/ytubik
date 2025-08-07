from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import structlog
import os

from app.models.database import get_db
from app.services.download_service import DownloadService
from app.services.youtube_service import YouTubeService
from app.tasks.download_tasks import download_video_task
from app.schemas.download_schemas import (
    DownloadRequest, 
    DownloadResponse, 
    DownloadStatus as DownloadStatusSchema,
    DownloadHistory,
    ErrorResponse
)
from app.models.download import DownloadStatus

logger = structlog.get_logger()
router = APIRouter()

def get_client_ip(request: Request) -> str:
    """Получает IP адрес клиента"""
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.client.host

@router.post("/download", response_model=DownloadResponse)
async def create_download(
    request: DownloadRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Создает новую загрузку видео"""
    
    client_ip = get_client_ip(http_request)
    download_service = DownloadService(db)
    youtube_service = YouTubeService()
    
    try:
        # Проверяем rate limiting
        rate_limit = download_service.check_rate_limit(client_ip)
        if not rate_limit['allowed']:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Превышен лимит загрузок",
                    "hourly_limit": rate_limit['hourly_limit'],
                    "daily_limit": rate_limit['daily_limit'],
                    "hourly_count": rate_limit['hourly_count'],
                    "daily_count": rate_limit['daily_count']
                }
            )
        
        # Валидируем видео
        validation = await youtube_service.validate_video(str(request.url))
        if not validation['valid']:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка валидации видео: {validation['error']}"
            )
        
        video_info = validation['info']
        video_id = youtube_service.extract_video_id(str(request.url))
        
        # Создаем запись загрузки
        download = download_service.create_download(
            youtube_url=str(request.url),
            video_id=video_id,
            format_type=request.format,
            quality=request.quality,
            audio_only=request.audio_only,
            client_ip=client_ip
        )
        
        # Обновляем информацию о видео
        download_service.update_video_info(download.id, video_info.dict())
        
        # Запускаем асинхронную задачу загрузки
        task = download_video_task.delay(download.id)
        
        logger.info("Создана новая загрузка",
                   download_id=download.id,
                   task_id=task.id,
                   client_ip=client_ip)
        
        return DownloadResponse(
            id=download.id,
            status=download.status,
            video_info=video_info,
            download_url=None,
            error_message=None,
            created_at=download.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Ошибка создания загрузки", error=str(e), client_ip=client_ip)
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")

@router.get("/download/{download_id}/status", response_model=DownloadStatusSchema)
async def get_download_status(download_id: str, db: Session = Depends(get_db)):
    """Получает статус загрузки"""
    
    download_service = DownloadService(db)
    download = download_service.get_download(download_id)
    
    if not download:
        raise HTTPException(status_code=404, detail="Загрузка не найдена")
    
    download_url = None
    if download.status == DownloadStatus.COMPLETED and download.file_name:
        download_url = f"/downloads/{download.file_name}"
    
    return DownloadStatusSchema(
        id=download.id,
        status=download.status,
        error_message=download.error_message,
        file_name=download.file_name,
        file_size=download.file_size,
        download_url=download_url
    )

@router.get("/download/{download_id}/file")
async def download_file(download_id: str, db: Session = Depends(get_db)):
    """Скачивает файл"""
    
    download_service = DownloadService(db)
    download = download_service.get_download(download_id)
    
    if not download:
        raise HTTPException(status_code=404, detail="Загрузка не найдена")
    
    if download.status != DownloadStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Загрузка еще не завершена")
    
    if not download.file_path or not os.path.exists(download.file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    
    return FileResponse(
        path=download.file_path,
        filename=download.file_name,
        media_type='application/octet-stream'
    )

@router.get("/downloads", response_model=DownloadHistory)
async def get_downloads_history(
    page: int = 1,
    per_page: int = 20,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """Получает историю загрузок"""
    
    if per_page > 100:
        per_page = 100
    
    client_ip = get_client_ip(request) if request else None
    download_service = DownloadService(db)
    
    downloads, total = download_service.get_downloads_history(
        page=page, 
        per_page=per_page,
        client_ip=client_ip
    )
    
    download_responses = []
    for download in downloads:
        video_info = None
        if download.video_title:
            video_info = {
                'video_id': download.video_id,
                'title': download.video_title,
                'description': download.video_description,
                'duration': download.video_duration,
                'thumbnail': download.video_thumbnail,
                'channel_name': download.channel_name,
                'view_count': download.view_count,
                'available_formats': []
            }
        
        download_url = None
        if download.status == DownloadStatus.COMPLETED and download.file_name:
            download_url = f"/downloads/{download.file_name}"
        
        download_responses.append(DownloadResponse(
            id=download.id,
            status=download.status,
            video_info=video_info,
            download_url=download_url,
            error_message=download.error_message,
            created_at=download.created_at
        ))
    
    return DownloadHistory(
        downloads=download_responses,
        total=total,
        page=page,
        per_page=per_page
    )
