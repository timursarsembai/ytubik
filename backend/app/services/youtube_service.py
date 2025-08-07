import yt_dlp
import os
import structlog
from typing import Dict, Optional, List
from urllib.parse import urlparse, parse_qs

from app.config.settings import settings
from app.schemas.download_schemas import VideoInfo

logger = structlog.get_logger()

class YouTubeService:
    """Сервис для работы с YouTube через yt-dlp"""
    
    def __init__(self):
        self.ydl_opts_info = {
            'quiet': True,
            'no_warnings': True,
            'extractaudio': False,
            'skip_download': True,
            # Добавляем настройки для обхода блокировок
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            # Используем cookies для лучшей совместимости
            'cookiefile': None,
            # Включаем экстракторы для лучшей поддержки
            'extractor_args': {
                'youtube': {
                    'player_client': ['web'],
                    'skip': ['dash'],
                }
            },
        }
    
    def extract_video_id(self, url: str) -> str:
        """Извлекает video_id из YouTube URL"""
        try:
            if 'youtu.be/' in url:
                return url.split('youtu.be/')[-1].split('?')[0]
            elif 'youtube.com/watch' in url:
                parsed = urlparse(url)
                return parse_qs(parsed.query)['v'][0]
            else:
                raise ValueError("Неверный формат YouTube URL")
        except Exception as e:
            logger.error("Ошибка извлечения video_id", url=url, error=str(e))
            raise ValueError(f"Не удалось извлечь video_id: {str(e)}")
    
    async def get_video_info(self, url: str) -> VideoInfo:
        """Получает информацию о видео"""
        return self._extract_video_info(url)
    
    def get_video_info_sync(self, url: str) -> dict:
        """Синхронная версия получения информации о видео для Celery"""
        video_info = self._extract_video_info(url)
        return video_info.dict()
    
    def _extract_video_info(self, url: str) -> VideoInfo:
        """Получает информацию о видео"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Получаем доступные форматы
                available_formats = []
                if 'formats' in info:
                    for fmt in info['formats'][:10]:  # Первые 10 форматов
                        format_info = {
                            'format_id': fmt.get('format_id'),
                            'ext': fmt.get('ext'),
                            'quality': fmt.get('format_note', 'unknown'),
                            'filesize': fmt.get('filesize'),
                            'vcodec': fmt.get('vcodec'),
                            'acodec': fmt.get('acodec'),
                        }
                        available_formats.append(format_info)
                
                video_info = VideoInfo(
                    video_id=self.extract_video_id(url),
                    title=info.get('title', 'Unknown'),
                    description=info.get('description'),
                    duration=info.get('duration'),
                    thumbnail=info.get('thumbnail'),
                    channel_name=info.get('uploader'),
                    view_count=info.get('view_count'),
                    available_formats=available_formats
                )
                
                logger.info("Информация о видео получена", 
                   video_id=video_info.video_id,
                   video_title=video_info.title)
                
                return video_info
                
        except Exception as e:
            logger.error("Ошибка получения информации о видео", url=url, error=str(e))
            raise ValueError(f"Не удалось получить информацию о видео: {str(e)}")
    
    def get_download_options(self, format_type: str, quality: str, audio_only: bool) -> Dict:
        """Создает опции для yt-dlp на основе запроса"""
        
        output_template = os.path.join(
            settings.DOWNLOAD_DIR, 
            '%(id)s_%(title)s.%(ext)s'
        )
        
        base_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            # Добавляем те же настройки для обхода блокировок
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'cookiefile': None,
            'extractor_args': {
                'youtube': {
                    'player_client': ['web'],
                    'skip': ['dash'],
                }
            },
            # Дополнительные настройки для стабильности
            'retries': 3,
            'fragment_retries': 3,
            'socket_timeout': 30,
        }
        
        if audio_only:
            base_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            })
        else:
            # Для видео
            if quality == 'best':
                format_selector = f'best[height<={1080}]'
            elif quality.endswith('p'):
                height = quality[:-1]
                format_selector = f'best[height<={height}]'
            else:
                format_selector = 'best'
            
            base_opts['format'] = format_selector
        
        return base_opts
    
    def get_alternative_download_options(self, format_type: str, quality: str, audio_only: bool) -> Dict:
        """Альтернативные опции с android клиентом для обхода блокировок"""
        
        output_template = os.path.join(
            settings.DOWNLOAD_DIR, 
            '%(id)s_%(title)s.%(ext)s'
        )
        
        opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': True,
            # Используем Android клиент - часто работает лучше
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],
                    'skip': ['dash'],
                }
            },
            'user_agent': 'com.google.android.youtube/17.31.35 (Linux; U; Android 11) gzip',
            'headers': {
                'User-Agent': 'com.google.android.youtube/17.31.35 (Linux; U; Android 11) gzip',
                'X-YouTube-Client-Name': '3',
                'X-YouTube-Client-Version': '17.31.35',
            },
            'retries': 5,
            'fragment_retries': 5,
            'socket_timeout': 30,
        }
        
        if audio_only:
            opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            })
        else:
            # Для видео - используем более простой формат для android
            if quality == 'best':
                format_selector = 'best[height<=720]'  # Ограничиваем качество для стабильности
            elif quality.endswith('p'):
                height = min(int(quality[:-1]), 720)  # Не выше 720p
                format_selector = f'best[height<={height}]'
            else:
                format_selector = 'best[height<=720]'
            
            opts['format'] = format_selector
        
        return opts
    
    async def validate_video(self, url: str) -> Dict:
        """Проверяет доступность видео и его параметры"""
        try:
            info = await self.get_video_info(url)
            
            # Проверка длительности
            if info.duration and info.duration > settings.MAX_VIDEO_DURATION_MINUTES * 60:
                raise ValueError(f"Видео слишком длинное. Максимум {settings.MAX_VIDEO_DURATION_MINUTES} минут")
            
            return {
                'valid': True,
                'info': info,
                'error': None
            }
            
        except Exception as e:
            return {
                'valid': False,
                'info': None,
                'error': str(e)
            }
