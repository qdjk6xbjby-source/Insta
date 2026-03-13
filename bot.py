import asyncio
import logging
import os
import re
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, URLInputFile
from aiogram.utils.media_group import MediaGroupBuilder

from downloader import get_instagram_media

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_USERS = os.getenv("ALLOWED_USERS", "")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Регулярное выражение для поиска ссылок Instagram
INSTAGRAM_REGEX = re.compile(r"(https?://(?:www\.)?instagram\.com/(?:p|reel|reels|tv|stories)/[A-Za-z0-9_-]+)")

# Инициализация бота
if not BOT_TOKEN or BOT_TOKEN == "СЮДА_ВСТАВЬ_ТОКЕН_НОВОГО_БОТА":
    log.error("BOT_TOKEN не настроен в .env!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def is_admin(user_id: int) -> bool:
    """Проверка, является ли пользователь админом (если нужно ограничить доступ)"""
    if not ALLOWED_USERS:
        return True # Если список пуст, разрешаем всем
    allowed_ids = [int(x.strip()) for x in ALLOWED_USERS.split(",") if x.strip()]
    return user_id in allowed_ids

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    if not is_admin(message.from_user.id):
         await message.answer("Извините, бот в стадии закрытого тестирования.")
         return
         
    await message.answer(
        "👋 Привет! Я скачиваю видео и фото из **Instagram**.\n\n"
        "Просто отправь мне ссылку на Reels, пост (Post) или Story!\n"
        "Пример: `https://www.instagram.com/reel/C1234567890/`"
    )

@dp.message(F.text)
async def handle_text(message: types.Message):
    """Обработка всех текстовых сообщений (поиск ссылок)"""
    if not is_admin(message.from_user.id):
        return

    # Ищем ссылку на инсту
    match = INSTAGRAM_REGEX.search(message.text)
    if not match:
        await message.answer("❌ Я не вижу здесь ссылку на Instagram Reels, Post или Story.")
        return

    url = match.group(1)
    
    # Отправляем статус "Печатает..." или сообщение ожидания
    status_msg = await message.answer("⏳ Скачиваю медиа... Пожалуйста, подождите.")
    
    # Запрашиваем медиа через API
    media_items = get_instagram_media(url)
    
    if not media_items:
        await status_msg.edit_text(
            "❌ Не удалось скачать медиа.\n"
            "Возможно, аккаунт закрыт (Private), ссылка неверная, или сервер перегружен."
        )
        return

    try:
        if len(media_items) == 1:
            # Одиночное медиа (фото или видео)
            item = media_items[0]
            if item["type"] == "video":
                await bot.send_video(chat_id=message.chat.id, video=URLInputFile(item["url"]))
            else:
                await bot.send_photo(chat_id=message.chat.id, photo=URLInputFile(item["url"]))
        else:
            # Карусель (несколько фото/видео)
            media_group = MediaGroupBuilder()
            for item in media_items:
                if item["type"] == "video":
                    media_group.add_video(media=URLInputFile(item["url"]))
                else:
                    media_group.add_photo(media=URLInputFile(item["url"]))
            
            await bot.send_media_group(chat_id=message.chat.id, media=media_group.build())
            
        # Удаляем статусное сообщение при успехе
        await status_msg.delete()
        log.info(f"Успешно отправлено {len(media_items)} медиа пользователю {message.from_user.id}")

    except Exception as e:
        log.error(f"Ошибка при отправке в Telegram: {e}")
        await status_msg.edit_text(f"❌ Ошибка отправки в Telegram: файл слишком большой или недоступен.")


async def main():
    log.info("Запуск Instagram Downloader Bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
