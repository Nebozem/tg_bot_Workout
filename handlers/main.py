from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import json
import os

router = Router()

# Загружаем программы
with open(os.path.join("data", "programs.json"), "r", encoding="utf-8") as f:
    programs = json.load(f)

# /start
@router.message(Command("start"))
async def start(message: types.Message):
    buttons = [KeyboardButton(text=program_name) for program_name in programs.keys()]
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[b] for b in buttons],
        resize_keyboard=True
    )
    await message.answer("Выберите программу тренировок:", reply_markup=keyboard)

# Обработчик выбора программы через lambda-фильтр
@router.message()
async def choose_program(message: types.Message):
    text = message.text
    if text in programs:
        first_day = programs[text]["days"][0]
        exercises = "\n".join(first_day["exercises"])
        await message.answer(f"{first_day['name']}:\n{exercises}")
    else:
        await message.answer("Пожалуйста, выберите программу из списка.")
