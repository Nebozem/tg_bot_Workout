from aiogram import Router, types
from handlers.weights import user_state, show_exercise, programs_data

router = Router()


@router.message(lambda m: m.text == "Следующий день")
async def next_day(message: types.Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return

    # Получаем все дни программы
    program_days = list(programs_data[state["program"]].keys())
    current_day_index = program_days.index(str(state["day"]))

    # Проверяем, есть ли следующий день
    if current_day_index + 1 < len(program_days):
        next_day_num = int(program_days[current_day_index + 1])
        state["day"] = next_day_num
        state["exercise_index"] = 0  # Сбрасываем индекс упражнения
        await message.answer(f"Переходим к дню {next_day_num}...")
        await show_exercise(user_id, message)
    else:
        await message.answer("Это последний день программы!")


@router.message(lambda m: m.text == "Предыдущий день")
async def prev_day(message: types.Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return

    # Получаем все дни программы
    program_days = list(programs_data[state["program"]].keys())
    current_day_index = program_days.index(str(state["day"]))

    # Проверяем, есть ли предыдущий день
    if current_day_index > 0:
        prev_day_num = int(program_days[current_day_index - 1])
        state["day"] = prev_day_num
        state["exercise_index"] = 0  # Сбрасываем индекс упражнения
        await message.answer(f"Возвращаемся к дню {prev_day_num}...")
        await show_exercise(user_id, message)
    else:
        await message.answer("Это первый день программы!")


@router.message(lambda m: m.text == "Повторить день")
async def repeat_day(message: types.Message):
    user_id = message.from_user.id
    state = user_state.get(user_id)

    if not state:
        await message.answer("Сначала выберите программу (/start)")
        return

    # Просто сбрасываем индекс упражнения
    state["exercise_index"] = 0
    await message.answer("Начинаем день заново...")
    await show_exercise(user_id, message)