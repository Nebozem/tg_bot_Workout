import os
from dotenv import load_dotenv

# Пытаемся загрузить из переменных окружения Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Если не найдено, пробуем локальный config.env (для разработки)
if not BOT_TOKEN:
    load_dotenv("config.env")
    BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")