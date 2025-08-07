#!/usr/bin/env python3
"""
Тестовый скрипт для проверки загрузки YouTube видео
"""

import sys
import os

# Добавляем путь к модулям backend
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.youtube_service import YouTubeService

def test_video_info():
    """Тестируем получение информации о видео"""
    print("🎬 Тестирование получения информации о видео...")
    
    service = YouTubeService()
    
    # Список тестовых видео
    test_videos = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo (первое видео на YouTube)
        "https://www.youtube.com/watch?v=9bZkp7q19f0",  # Gangnam Style
    ]
    
    for url in test_videos:
        try:
            print(f"\n📹 Тестируем: {url}")
            info = service.get_video_info_sync(url)
            print(f"   ✅ Название: {info.get('title', 'N/A')}")
            print(f"   ✅ Длительность: {info.get('duration', 'N/A')} сек")
            print(f"   ✅ Канал: {info.get('channel_name', 'N/A')}")
            return True
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            continue
    
    print("   ❌ Все тестовые видео не удалось обработать")
    return False

def test_download_options():
    """Тестируем создание опций для загрузки"""
    print("\n⚙️ Тестирование опций загрузки...")
    
    service = YouTubeService()
    
    try:
        # Тестируем различные опции
        opts_video = service.get_download_options("mp4", "720p", False)
        opts_audio = service.get_download_options("mp3", "best", True)
        opts_alt = service.get_alternative_download_options("mp4", "480p", False)
        
        print("   ✅ Опции для видео MP4 720p созданы")
        print("   ✅ Опции для аудио MP3 созданы")
        print("   ✅ Альтернативные опции созданы")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка создания опций: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🔧 Тестирование исправлений YouTube downloader\n")
    
    tests = [
        ("Получение информации о видео", test_video_info),
        ("Создание опций загрузки", test_download_options),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"--- {test_name} ---")
        if test_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Исправления работают.")
        print("\n💡 Рекомендации:")
        print("1. Перезапустите Celery worker")
        print("2. Попробуйте скачать тестовое видео")
        print("3. Если проблемы сохраняются, попробуйте другие видео")
        return True
    else:
        print("⚠️ Некоторые тесты не пройдены.")
        print("\n💡 Возможные решения:")
        print("1. Проверьте интернет-соединение")
        print("2. YouTube может блокировать запросы")
        print("3. Попробуйте позже или с VPN")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
