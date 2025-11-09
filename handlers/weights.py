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

async def start_day_workout(user_id: int, program: str, day: int, message: types.Message, state: FSMContext = None):
    user_state[user_id] = {"program": program, "day": day, "exercise_index": 0}

    exercises = programs_data[program].get(str(day))
    if not exercises:
        await message.answer("День не найден в программе")
        return

    text = f"День {day} — упражнения:\n"
    for ex in exercises:
        last_weight = get_last_weight(user_id, ex["name"])
        text += f"- {ex['name']} (вес: {last_weight} кг)\n"

    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Следующий день"), types.KeyboardButton(text="Предыдущий день")],
            [types.KeyboardButton(text="Следующее упражнение"), types.KeyboardButton(text="Ввести новый вес")]
        ],
        resize_keyboard=True
    )
    await message.answer(text, reply_markup=kb)

@router.message(lambda m: m.text == "Следующий день")
async def next_day(message: types.Message):
    state = user_state.get(message.from_user.id)
    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return
    state["day"] += 1
    await start_day_workout(message.from_user.id, state["program"], state["day"], message)

@router.message(lambda m: m.text == "Предыдущий день")
async def prev_day(message: types.Message):
    state = user_state.get(message.from_user.id)
    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return
    state["day"] = max(1, state["day"] - 1)
    await start_day_workout(message.from_user.id, state["program"], state["day"], message)

@router.message(lambda m: m.text == "Следующее упражнение")
async def next_exercise(message: types.Message):
    state = user_state.get(message.from_user.id)
    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return
    exercises = programs_data[state["program"]].get(str(state["day"]))
    state["exercise_index"] = (state.get("exercise_index", 0) + 1) % len(exercises)
    ex = exercises[state["exercise_index"]]
    last_weight = get_last_weight(message.from_user.id, ex["name"])
    await message.answer(f"Следующее упражнение: {ex['name']} (вес: {last_weight} кг)")

@router.message(lambda m: m.text == "Ввести новый вес")
async def enter_weight(message: types.Message, state: FSMContext):
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
    if not user:
        await message.answer("Сначала выберите программу (/start)")
        return

    exercises = programs_data[user["program"]].get(str(user["day"]))
    ex = exercises[user.get("exercise_index", 0)]
    save_weight(message.from_user.id, ex["name"], weight)
    await state.clear()
    await message.answer(f"Вес {weight} кг для упражнения {ex['name']} сохранён!")
