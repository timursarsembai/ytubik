import os
import re
from typing import Optional

def sanitize_filename(filename: str) -> str:
    """Очищает имя файла от недопустимых символов"""
    # Удаляем недопустимые символы
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Ограничиваем длину
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    return sanitized

def get_file_size_mb(file_path: str) -> Optional[float]:
    """Возвращает размер файла в MB"""
    try:
        if os.path.exists(file_path):
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
    except Exception:
        pass
    return None

def format_duration(seconds: int) -> str:
    """Форматирует длительность в читаемый вид"""
    if not seconds:
        return "Unknown"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def format_file_size(size_mb: float) -> str:
    """Форматирует размер файла"""
    if size_mb < 1:
        return f"{size_mb * 1024:.1f} KB"
    elif size_mb < 1024:
        return f"{size_mb:.1f} MB"
    else:
        return f"{size_mb / 1024:.1f} GB"
