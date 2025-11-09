import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from config import BOT_TOKEN
from handlers.main import router

async def main():
    # создаём объект с настройками по умолчанию
    default_props = DefaultBotProperties(parse_mode="HTML")

    # создаём бот с default_props
    bot = Bot(token=BOT_TOKEN, default=default_props)
    dp = Dispatcher()
    dp.include_router(router)

    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
а