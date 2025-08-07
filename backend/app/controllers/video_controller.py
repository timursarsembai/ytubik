from fastapi import APIRouter, HTTPException
import structlog

from app.services.youtube_service import YouTubeService
from app.schemas.download_schemas import VideoInfoRequest, VideoInfo

logger = structlog.get_logger()
router = APIRouter()

@router.post("/video/info", response_model=VideoInfo)
async def get_video_info(request: VideoInfoRequest):
    """Получает информацию о YouTube видео без загрузки"""
    
    youtube_service = YouTubeService()
    
    try:
        video_info = await youtube_service.get_video_info(str(request.url))
        
        logger.info("Получена информация о видео",
                   video_id=video_info.video_id,
                   title=video_info.title)
        
        return video_info
        
    except Exception as e:
        logger.error("Ошибка получения информации о видео", 
                    url=str(request.url), 
                    error=str(e))
        raise HTTPException(
            status_code=400, 
            detail=f"Не удалось получить информацию о видео: {str(e)}"
        )
