import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from config import BOT_TOKEN
from db.db_helper import init_db
from handlers import programs, weights, navigation


async def main():
    # Инициализация БД
    init_db()

    # Создание сессии с таймаутом
    session = AiohttpSession(
        timeout=30
    )

    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher()

    # Регистрация роутеров
    dp.include_router(programs.router)
    dp.include_router(weights.router)
    dp.include_router(navigation.router)

    print("🚀 Бот запущен на Railway...")

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())