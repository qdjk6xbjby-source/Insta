import os
import requests
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения из корня папки проекта
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger(__name__)

def get_instagram_media(url: str) -> list:
    """
    Отправляет запрос к RapidAPI и возвращает список ссылок на медиа-файлы.
    Возвращает список словарей: [{'type': 'video'|'image', 'url': 'https...'}], 
    либо пустой список в случае ошибки.
    """
    if not RAPIDAPI_KEY or not RAPIDAPI_HOST:
        log.error("RapidAPI ключи не настроены в .env!")
        return []

    # Используем конкретный эндпоинт от пользователя
    api_url = f"https://{RAPIDAPI_HOST}/postdetail/"
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "Content-Type": "application/json"
    }
    
    querystring = {"code_or_url": url}

    log.info(f"Запрос к API для ссылки: {url}")
    
    try:
        response = requests.get(api_url, headers=headers, params=querystring, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        media_list = []
        
        # Рекурсивная функция для поиска URL-адресов видео и картинок в сложном JSON
        def find_media_urls(obj):
            urls = []
            if isinstance(obj, dict):
                # Если в словаре есть 'video_versions', берем лучшее качество
                if 'video_versions' in obj and isinstance(obj['video_versions'], list) and len(obj['video_versions']) > 0:
                    urls.append({'type': 'video', 'url': obj['video_versions'][0].get('url')})
                # Если это карусель, ищем внутри
                elif 'carousel_media' in obj and isinstance(obj['carousel_media'], list):
                    for item in obj['carousel_media']:
                        urls.extend(find_media_urls(item))
                # Если есть image_versions2 (фото), берем лучшее качество, только если это не видео
                elif 'image_versions2' in obj and 'video_versions' not in obj:
                    candidates = obj['image_versions2'].get('candidates', [])
                    if candidates and isinstance(candidates, list):
                        urls.append({'type': 'image', 'url': candidates[0].get('url')})
                
                # Запасной вариант (поиск всех url, если структура неизвестна)
                elif 'url' in obj and isinstance(obj['url'], str):
                    if '.mp4' in obj['url'] or 'video' in obj.get('type', ''):
                        urls.append({'type': 'video', 'url': obj['url']})
                    elif '.jpg' in obj['url'] or '.webp' in obj['url']:
                        urls.append({'type': 'image', 'url': obj['url']})
                else:
                    for k, v in obj.items():
                        urls.extend(find_media_urls(v))
            elif isinstance(obj, list):
                for item in obj:
                    urls.extend(find_media_urls(item))
            return urls

        found_media = find_media_urls(data)
        
        # Убираем дубликаты, сохраняя порядок
        seen_urls = set()
        for media in found_media:
            if media['url'] and media['url'] not in seen_urls:
                seen_urls.add(media['url'])
                media_list.append(media)
                
        if not media_list:
            log.warning(f"Не удалось найти медиа в ответе API: {data.get('message', 'No message')}")
        
        return media_list
            
    except requests.exceptions.RequestException as e:
        log.error(f"Ошибка запроса к RapidAPI: {e}")
        return []
    except Exception as e:
        log.error(f"Неизвестная ошибка при обработке: {e}")
        return []
