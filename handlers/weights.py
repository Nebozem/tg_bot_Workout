from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import json
from datetime import datetime
from db.db_helper import save_weight, get_last_weight, get_weight_history

router = Router()
user_state = {}

with open("data/programs.json", encoding="utf-8") as f:
    programs_data = json.load(f)

class WeightInput(StatesGroup):
    waiting_for_weight = State()

class DayInput(StatesGroup):
    waiting_for_day_number = State()

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
        # ДЕНЬ ЗАВЕРШЕН - показываем кнопки навигации
        kb = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Следующий день"), types.KeyboardButton(text="Предыдущий день")],
                [types.KeyboardButton(text="Выбрать день по номеру"), types.KeyboardButton(text="Повторить день")]
            ],
            resize_keyboard=True
        )
        await message.answer("День завершён! Можно перейти к следующему дню.", reply_markup=kb)
        return

    ex = exercises[idx]
    
    # Определяем тип упражнения
    if ex.get("type") == "superset":
        await show_superset(user_id, ex, message)
    elif ex.get("type") == "cardio":
        await show_cardio(ex, message)
    else:
        await show_single_exercise(user_id, ex, message)

async def show_single_exercise(user_id: int, ex: dict, message: types.Message):
    """Показывает обычное упражнение"""
    last_weight = get_last_weight(user_id, ex["name"])
    
    text = f"💪 {ex['name']}\n"
    text += f"Подходы: {ex.get('sets', '3x8')}\n"
    text += f"Текущий вес: {last_weight} кг"
    
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Следующее упражнение"), types.KeyboardButton(text="Ввести новый вес")],
            [types.KeyboardButton(text="📊 Посмотреть статистику по упражнению")]
        ],
        resize_keyboard=True
    )
    await message.answer(text, reply_markup=kb)

async def show_superset(user_id: int, superset: dict, message: types.Message):
    """Показывает супер-сет"""
    state = user_state[user_id]
    exercises_list = superset["exercises"]
    current_sub_index = state.get("superset_index", 0)
    
    if current_sub_index >= len(exercises_list):
        # Супер-сет завершен - показываем сообщение и переходим дальше
        state["superset_index"] = 0
        await message.answer("✅ Супер-сет закончен, переходим к следующему упражнению")
        await next_exercise_logic(user_id, message)
        return
    
    sub_ex = exercises_list[current_sub_index]
    last_weight = get_last_weight(user_id, sub_ex["name"])
    
    text = f"🔁 {superset['name']}\n"
    text += f"Упражнение {current_sub_index + 1}/{len(exercises_list)}: {sub_ex['name']}\n"
    text += f"Подходы: {sub_ex.get('sets', '3x8')}\n"
    text += f"Текущий вес: {last_weight} кг"
    
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Следующее упражнение в супер-сете")],
            [types.KeyboardButton(text="Ввести вес для этого упражнения")],
            [types.KeyboardButton(text="📊 Посмотреть статистику по упражнению")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(text, reply_markup=kb)

async def show_cardio(cardio: dict, message: types.Message):
    """Показывает кардио задание"""
    text = f"🏃‍♂️ {cardio['name']}"
    
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Следующее упражнение")],
        ],
        resize_keyboard=True
    )
    await message.answer(text, reply_markup=kb)

async def show_statistics(user_id: int, exercise_name: str, message: types.Message):
    """Показывает статистику по упражнению"""
    history = get_weight_history(user_id, exercise_name)
    
    if not history:
        text = f"📊 Статистика по упражнению '{exercise_name}'\n"
        text += "Ещё нет записей о весах. Начните тренироваться!"
    else:
        text = f"📊 Статистика по упражнению '{exercise_name}'\n\n"
        for i, (weight, date) in enumerate(history, 1):
            # Форматируем дату для красоты
            date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            formatted_date = date_obj.strftime("%d.%m.%Y")
            text += f"{i}. {weight} кг - {formatted_date}\n"
        
        # Добавляем прогресс
        if len(history) > 1:
            first_weight = history[-1][0]  # Самый старый вес
            last_weight = history[0][0]    # Самый новый вес
            progress = last_weight - first_weight
            if progress > 0:
                text += f"\n📈 Прогресс: +{progress} кг"
            elif progress < 0:
                text += f"\n📉 Изменение: {progress} кг"
            else:
                text += f"\n➡️ Вес не изменился"
    
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="↩️ Вернуться к упражнению")],
        ],
        resize_keyboard=True
    )
    
    await message.answer(text, reply_markup=kb)

@router.message(lambda m: m.text == "📊 Посмотреть статистику по упражнению")
async def show_exercise_stats(message: types.Message):
    """Показывает статистику для текущего упражнения"""
    user_id = message.from_user.id
    state = user_state.get(user_id)
    
    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return

    exercises = programs_data[state["program"]].get(str(state["day"]))
    idx = state.get("exercise_index", 0)
    
    if idx >= len(exercises):
        await message.answer("День завершен, статистика недоступна")
        return

    ex = exercises[idx]
    
    # Определяем название упражнения в зависимости от типа
    if ex.get("type") == "superset":
        sub_index = state.get("superset_index", 0)
        if sub_index < len(ex["exercises"]):
            exercise_name = ex["exercises"][sub_index]["name"]
        else:
            await message.answer("Супер-сет завершен, статистика недоступна")
            return
    elif ex.get("type") == "cardio":
        await message.answer("Для кардио статистика не ведется")
        return
    else:
        exercise_name = ex["name"]
    
    await show_statistics(user_id, exercise_name, message)

@router.message(lambda m: m.text == "↩️ Вернуться к упражнению")
async def return_to_exercise(message: types.Message):
    """Возвращает к текущему упражнению"""
    user_id = message.from_user.id
    state = user_state.get(user_id)
    
    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return
    
    await show_exercise(user_id, message)

@router.message(lambda m: m.text == "Следующее упражнение")
async def next_exercise(message: types.Message):
    await next_exercise_logic(message.from_user.id, message)

async def next_exercise_logic(user_id: int, message: types.Message):
    """Общая логика перехода к следующему упражнению"""
    state = user_state.get(user_id)
    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return

    state["exercise_index"] = state.get("exercise_index", 0) + 1
    await show_exercise(user_id, message)

@router.message(lambda m: m.text == "Следующее упражнение в супер-сете")
async def next_superset_exercise(message: types.Message):
    """Переход к следующему упражнению в супер-сете"""
    user_id = message.from_user.id
    state = user_state[user_id]
    state["superset_index"] = state.get("superset_index", 0) + 1
    await show_exercise(user_id, message)

@router.message(lambda m: m.text == "Ввести новый вес")
async def enter_weight(message: types.Message, state: FSMContext):
    user = user_state.get(message.from_user.id)
    if not user:
        await message.answer("Сначала выберите программу (/start)")
        return

    await state.set_state(WeightInput.waiting_for_weight)
    await message.answer("Введите новый рабочий вес (кг):")

@router.message(lambda m: m.text == "Ввести вес для этого упражнения")
async def enter_superset_weight(message: types.Message, state: FSMContext):
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

    # Если это супер-сет, берем текущее упражнение из супер-сета
    if ex.get("type") == "superset":
        sub_index = user.get("superset_index", 0)
        sub_ex = ex["exercises"][sub_index]
        exercise_name = sub_ex["name"]
    else:
        exercise_name = ex["name"]

    save_weight(message.from_user.id, exercise_name, weight)
    await state.clear()
    await show_exercise(message.from_user.id, message)

@router.message(lambda m: m.text == "Выбрать день по номеру")
async def select_day_by_number(message: types.Message):
    user = user_state.get(message.from_user.id)
    if not user:
        await message.answer("Сначала выберите программу (/start)")
        return

    # Получаем доступные дни для текущей программы
    program_days = list(programs_data[user["program"]].keys())
    max_day = max(map(int, program_days))
    
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="1"), types.KeyboardButton(text="2"), types.KeyboardButton(text="3")],
            [types.KeyboardButton(text="4"), types.KeyboardButton(text="5"), types.KeyboardButton(text="6")],
            [types.KeyboardButton(text="↩️ Назад к тренировке")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(f"Введите номер дня (от 1 до {max_day}):", reply_markup=kb)

@router.message(lambda m: m.text == "↩️ Назад к тренировке")
async def back_to_workout(message: types.Message):
    """Возврат к текущей тренировке"""
    user_id = message.from_user.id
    state = user_state.get(user_id)
    
    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return
    
    await show_exercise(user_id, message)

@router.message(lambda m: m.text and m.text.isdigit())
async def handle_day_number_input(message: types.Message):
    """Обрабатывает ввод номера дня напрямую"""
    user_id = message.from_user.id
    state = user_state.get(user_id)
    
    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return
    
    try:
        day_number = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число")
        return

    program_days = list(programs_data[state["program"]].keys())
    
    # Проверяем, существует ли такой день
    if str(day_number) not in program_days:
        max_day = max(map(int, program_days))
        await message.answer(f"День {day_number} не найден. Введите номер от 1 до {max_day}")
        return

    # Устанавливаем выбранный день
    state["day"] = day_number
    state["exercise_index"] = 0
    state["superset_index"] = 0
    
    await message.answer(f"Переходим к дню {day_number}...")
    await show_exercise(user_id, message)

async def start_day_workout(user_id: int, program: str, day: int, message: types.Message):
    """Начало дня — сбрасываем все индексы"""
    user_state[user_id] = {
        "program": program, 
        "day": day, 
        "exercise_index": 0,
        "superset_index": 0
    }
    await show_exercise(user_id, message)
