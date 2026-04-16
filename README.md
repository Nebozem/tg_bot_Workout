![Python](https://img.shields.io/badge/Python-3.11-blue)
![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green)
![SQLite](https://img.shields.io/badge/SQLite-3-blue)

# tg_bot_Workout

Telegram-бот для отслеживания тренировок, прогресса весов и выполнения программ с поддержкой супер-сетов и кардио.

## 📋 Функционал

- 📅 **Тренировочные программы** — предустановленные программы с днями и упражнениями
- 💪 **Супер-сеты** — поддержка групповых упражнений
- 🏃 **Кардио** — отдельный тип заданий
- 📊 **Статистика весов** — история прогресса по каждому упражнению
- 💾 **Сохранение результатов** — все рабочие веса хранятся в БД
- 🧭 **Навигация** — переход между днями, повтор дня, выбор дня по номеру

Ниже приведён пример использования бота в Telegram на Android.

## Скриншоты использования

## Шаг 1 — Выбор программы, переход между упражнениями, установка веса

<img width="1080" height="2171" alt="1000022802" src="https://github.com/user-attachments/assets/0f9b1890-0375-42fa-9c92-509137f6065f" />

## Шаг 2 — Выбор дня по номеру

<img width="1080" height="2159" alt="1000022804" src="https://github.com/user-attachments/assets/80044f8a-7246-4cc9-8d38-8e82f75972c7" />

## Шаг 3 — Просмотр статистики по упражнению

<img width="1080" height="2169" alt="1000022806" src="https://github.com/user-attachments/assets/4e3f9059-0001-403f-939c-35a94e898d7d" />

## 🛠 Технологический стек

| Технология | Назначение |
|------------|------------|
| Python 3.11+ | Основной язык |
| Aiogram 3.x | Асинхронный фреймворк для Telegram Bot API |
| Aiohttp | Асинхронный HTTP клиент |
| SQLite | Хранение весов и истории тренировок |
| JSON | Конфигурация тренировочных программ |
| asyncio | Асинхронное выполнение |
| python-dotenv | Управление переменными окружения |

### DevOps и деплой
- **Linux (Ubuntu 24.04)** — серверная платформа
- **Systemd** — автозапуск и управление процессом
- **SSH** — удаленное управление
- **Git** — контроль версий

## 📁 Структура проекта

```
tg_bot_Workout/
├── bot.py
├── workout_bot.py
├── config.py
├── config.env
├── requirements.txt
├── data/
│   └── programs.json
├── db.sqlite
├── db/
│   └── db_helper.py
├── handlers/
│   ├── navigation.py
│   ├── programs.py
│   └── weights.py
```

## 📦 Установка и запуск

### Локально

# Клонировать репозиторий
git clone https://github.com/Nebozem/tg_bot_Workout
cd tg_bot_Workout

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Создать config.env с токеном бота
echo "BOT_TOKEN=your_telegram_bot_token" > config.env

# Запустить бота
python3 bot.py

На VPS (Beget / Ubuntu)
bash
# Загрузить проект
scp -r tg_bot_Workout botadmin@your-server:/home/botadmin/projects/

# На сервере
cd /home/botadmin/projects/tg_bot_Workout
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Запуск через systemd (автозапуск)
sudo nano /etc/systemd/system/fitness-bot.service
sudo systemctl daemon-reload
sudo systemctl enable fitness-bot.service
sudo systemctl start fitness-bot.service

## 📄 Формат `programs.json`

```json
{
  "program_1": {
    "1": [
      {
        "type": "single",
        "name": "Шаги выпадами",
        "default_weight": 0,
        "sets": "1x20 без веса и 3x12 на 100%"
      },
      {
        "type": "superset",
        "name": "Супер-сет: Ноги и пуловер",
        "exercises": [
          {
            "name": "Жим ногами",
            "default_weight": 0,
            "sets": "4x12"
          },
          {
            "name": "Пуловер с гантелью",
            "default_weight": 0,
            "sets": "4x12"
          }
        ]
      },
      {
        "type": "cardio",
        "name": "Бег 10 минут"
      }
    ]
  }
}
```

## Управление ботом

Все действия выполняются через кнопки. Бот не требует запоминания команд.

## 🎮 Управление ботом

Все действия выполняются через кнопки — бот не требует запоминания команд.

| Действие | Кнопка |
|:---------|:-------|
Следующее упражнение | `Следующее упражнение`
Следующее упражнение в супер-сете | `Следующее упражнение в супер-сете`
Записать рабочий вес | `Ввести новый вес`
Посмотреть прогресс | `📊 Посмотреть статистику по упражнению`
Вернуться к упражнению | `↩️ Вернуться к упражнению`
Перейти к следующему дню | `Следующий день`
Вернуться к предыдущему дню | `Предыдущий день`
Перейти к любому дню | `Выбрать день по номеру`
Пройти день заново | `Повторить день`

> 💡 **Единственная текстовая команда:** `/start` — начать тренировку и выбрать программу.

## 🤖 Демо

Попробовать бота: https://t.me/Gym_prog_bot
