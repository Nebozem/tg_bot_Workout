from aiogram import Router, types

router = Router()

@router.message(lambda m: m.text == "Следующий день")
async def next_day(message: types.Message):
    await message.answer("Переходим к следующему дню...")

@router.message(lambda m: m.text == "Предыдущий день")
async def prev_day(message: types.Message):
    await message.answer("Возвращаемся к предыдущему дню...")
