#!/usr/bin/env python3
"""
Тестовый скрипт для проверки основных функций YouTube downloader
"""

import sys
import os

# Добавляем путь к модулям backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Тестируем импорты всех модулей"""
    print("🧪 Тестирование импортов...")
    
    try:
        # Основные зависимости
        import fastapi
        import uvicorn
        import yt_dlp
        import celery
        import redis
        import sqlalchemy
        import pydantic
        print("✅ Основные зависимости: OK")
        
        # Проверяем наши модули
        from app.main import app
        from app.services.youtube_service import YouTubeService
        from app.models.download import Download
        print("✅ Модули приложения: OK")
        
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_youtube_service():
    """Тестируем YouTube сервис"""
    print("🎥 Тестирование YouTube сервиса...")
    
    try:
        from app.services.youtube_service import YouTubeService
        
        service = YouTubeService()
        
        # Тестовое видео (короткое)
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll (короткое видео для теста)
        
        print(f"   Получение информации о видео: {test_url}")
        # Используем синхронную версию для тестов
        info = service.get_video_info_sync(test_url)
        
        if info:
            print(f"   ✅ Название: {info.get('title', 'N/A')}")
            print(f"   ✅ Длительность: {info.get('duration', 'N/A')} сек")
            print(f"   ✅ Доступные форматы: {len(info.get('formats', []))}")
            return True
        else:
            print("   ❌ Не удалось получить информацию о видео")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка YouTube сервиса: {e}")
        return False

def test_config():
    """Тестируем конфигурацию"""
    print("⚙️ Тестирование конфигурации...")
    
    try:
        from app.config.settings import settings
        
        print(f"   ✅ Database URL: {settings.DATABASE_URL[:50]}...")
        print(f"   ✅ Redis URL: {settings.REDIS_URL}")
        print(f"   ✅ Download Directory: {settings.DOWNLOAD_DIR}")
        
        # Проверяем, что директория существует
        if not os.path.exists(settings.DOWNLOAD_DIR):
            os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)
            print(f"   ✅ Создана директория для загрузок: {settings.DOWNLOAD_DIR}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка конфигурации: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🔍 Запуск тестов YouTube Downloader MVP\n")
    
    tests = [
        ("Импорты", test_imports),
        ("Конфигурация", test_config),
        ("YouTube сервис", test_youtube_service),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Проект готов к запуску.")
        print("\n🚀 Для запуска используйте:")
        print("   ./start_dev.sh")
        return True
    else:
        print("⚠️ Некоторые тесты не пройдены. Проверьте зависимости.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
