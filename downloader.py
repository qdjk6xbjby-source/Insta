import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

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

    # Endpoint (может отличаться в зависимости от выбранного API на RapidAPI)
    # Используем универсальный эндпоинт для скачивания
    api_url = f"https://{RAPIDAPI_HOST}/instagram/download"
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    querystring = {"url": url}

    log.info(f"Запрос к API для ссылки: {url}")
    
    try:
        response = requests.get(api_url, headers=headers, params=querystring, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Парсинг ответа (структура зависит от конкретного API)
        # Предполагаем типичную структуру: {"data": [{"type": "video", "url": "..."}]}
        if "data" in data and isinstance(data["data"], list):
            media_list = []
            for item in data["data"]:
                media_type = "video" if "video" in item.get("type", "").lower() or ".mp4" in item.get("url", "") else "image"
                media_list.append({
                    "type": media_type,
                    "url": item.get("url", item.get("download_url"))
                })
            return media_list
        else:
            log.warning(f"Неожиданный ответ от API: {data}")
            return []
            
    except requests.exceptions.RequestException as e:
        log.error(f"Ошибка запроса к RapidAPI: {e}")
        return []
    except Exception as e:
        log.error(f"Неизвестная ошибка при обработке: {e}")
        return []
