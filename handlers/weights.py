from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import json
from db.db_helper import save_weight, get_last_weight

router = Router()
user_state = {}

with open("data/programs.json", encoding="utf-8") as f:
    programs_data = json.load(f)

class WeightInput(StatesGroup):
    waiting_for_weight = State()

async def show_exercise(user_id: int, message: types.Message):
    """Показывает текущее упражнение в дне."""
    state = user_state.get(user_id)
    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return

    exercises = programs_data[state["program"]].get(str(state["day"]))
    if not exercises:
        await message.answer("День не найден")
        return

    idx = state.get("exercise_index", 0)
    if idx >= len(exercises):
        await message.answer("День завершён! Можно перейти к следующему дню.")
        return

    ex = exercises[idx]
    last_weight = get_last_weight(user_id, ex["name"])

    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Следующее упражнение"), types.KeyboardButton(text="Ввести новый вес")],
        ],
        resize_keyboard=True
    )
    await message.answer(f"Упражнение: {ex['name']} (текущий вес: {last_weight} кг)", reply_markup=kb)

@router.message(lambda m: m.text == "Следующее упражнение")
async def next_exercise(message: types.Message):
    state = user_state.get(message.from_user.id)
    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return

    state["exercise_index"] = state.get("exercise_index", 0) + 1
    exercises = programs_data[state["program"]].get(str(state["day"]))
    if state["exercise_index"] >= len(exercises):
        await message.answer("День завершён! Можно перейти к следующему дню.")
        return

    await show_exercise(message.from_user.id, message)

@router.message(lambda m: m.text == "Ввести новый вес")
async def enter_weight(message: types.Message, state: FSMContext):
    user = user_state.get(message.from_user.id)
    if not user:
        await message.answer("Сначала выберите программу (/start)")
        return

    await state.set_state(WeightInput.waiting_for_weight)
    await message.answer("Введите новый рабочий вес (кг):")

@router.message(WeightInput.waiting_for_weight)
async def save_new_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Пожалуйста, введите число")
        return

    user = user_state.get(message.from_user.id)
    exercises = programs_data[user["program"]].get(str(user["day"]))
    idx = user.get("exercise_index", 0)
    ex = exercises[idx]

    save_weight(message.from_user.id, ex["name"], weight)
    await state.clear()
    await show_exercise(message.from_user.id, message)

async def start_day_workout(user_id: int, program: str, day: int, message: types.Message):
    """Начало дня — первый индекс упражнения = 0"""
    user_state[user_id] = {"program": program, "day": day, "exercise_index": 0}
    await show_exercise(user_id, message)