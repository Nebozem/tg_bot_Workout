from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from handlers.weights import start_day_workout, user_state, programs_data

router = Router()

class ProgramState(StatesGroup):
    waiting_for_day_selection = State()

def get_program_kb():
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Программа 1")],
            [types.KeyboardButton(text="Программа 2")],
            [types.KeyboardButton(text="Выбрать день по номеру")]
        ],
        resize_keyboard=True
    )
    return kb

def get_day_selection_kb():
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Начать с дня 1")],
            [types.KeyboardButton(text="Выбрать другой день")]
        ],
        resize_keyboard=True
    )
    return kb

@router.message(lambda m: m.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer("Выберите программу тренировок:", reply_markup=get_program_kb())

@router.message(lambda m: m.text in ["Программа 1", "Программа 2"])
async def select_program(message: types.Message, state: FSMContext):
    program = "program_1" if message.text == "Программа 1" else "program_2"
    
    # Сохраняем программу в состоянии
    await state.update_data(selected_program=program)
    
    # Показываем доступные дни
    program_days = list(programs_data[program].keys())
    max_day = max(map(int, program_days))
    
    text = f"Выбрана {message.text}\n"
    text += f"Доступно дней: {len(program_days)} (1-{max_day})\n\n"
    text += "Хотите начать с дня 1 или выбрать другой день?"
    
    await message.answer(text, reply_markup=get_day_selection_kb())
    await state.set_state(ProgramState.waiting_for_day_selection)

@router.message(ProgramState.waiting_for_day_selection)
async def handle_day_selection(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    program = user_data.get("selected_program")
    
    if not program:
        await message.answer("Сначала выберите программу (/start)")
        return
    
    if message.text == "Начать с дня 1":
        # Начинаем с дня 1
        await state.clear()
        await start_day_workout(message.from_user.id, program, 1, message)
    
    elif message.text == "Выбрать другой день":
        # Запрашиваем номер дня
        program_days = list(programs_data[program].keys())
        max_day = max(map(int, program_days))
        
        kb = types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="1"), types.KeyboardButton(text="2"), types.KeyboardButton(text="3")],
                [types.KeyboardButton(text="4"), types.KeyboardButton(text="5"), types.KeyboardButton(text="6")],
                [types.KeyboardButton(text="↩️ Назад к выбору программы")]
            ],
            resize_keyboard=True
        )
        
        await message.answer(f"Введите номер дня (1-{max_day}):", reply_markup=kb)
    
    elif message.text == "↩️ Назад к выбору программы":
        await state.clear()
        await cmd_start(message)
    
    elif message.text.isdigit():
        # Обрабатываем ввод номера дня
        try:
            day_number = int(message.text)
        except ValueError:
            await message.answer("Пожалуйста, введите число")
            return

        program_days = list(programs_data[program].keys())
        
        if str(day_number) not in program_days:
            max_day = max(map(int, program_days))
            await message.answer(f"День {day_number} не найден. Введите номер от 1 до {max_day}")
            return

        # Запускаем выбранный день
        await state.clear()
        await start_day_workout(message.from_user.id, program, day_number, message)
    
    else:
        await message.answer("Пожалуйста, используйте кнопки для выбора")
