import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from config import BOT_TOKEN
from db.db_helper import init_db
from handlers import programs, weights, navigation

async def main():
    init_db()

    session = AiohttpSession()
    bot = Bot(token=BOT_TOKEN, session=session)

    dp = Dispatcher()
    dp.include_router(programs.router)
    dp.include_router(weights.router)
    dp.include_router(navigation.router)

    print("Бот запущен...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
