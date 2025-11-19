from aiogram import Router, types
from handlers.weights import start_day_workout

router = Router()

def get_program_kb():
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Программа 1")],
            [types.KeyboardButton(text="Программа 2")]
        ],
        resize_keyboard=True
    )
    return kb

@router.message(lambda m: m.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer("Выберите программу тренировок:", reply_markup=get_program_kb())

@router.message(lambda m: m.text in ["Программа 1", "Программа 2"])
async def select_program(message: types.Message):
    program = "program_1" if message.text == "Программа 1" else "program_2"
    await start_day_workout(message.from_user.id, program, 1, message)
