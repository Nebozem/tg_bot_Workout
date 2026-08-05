# tg_bot_Workout

Telegram-бот для ведения силовых тренировок по готовым программам.  
Хранит рабочие веса по упражнениям, показывает статистику прогресса, поддерживает супер-сеты и кардио-блоки.

> Да, выбор дня по номеру реализован в `handlers/weights.py`: кнопка `Выбрать день по номеру` выводит запрос на ввод номера дня и переводит пользователя на выбранный день.

## Что есть в проекте

- 2 программы тренировок (`data/programs.json`)
- Выбор дня после выбора программы
- Навигация по упражнениям, дням и супер-сетам
- Ввод и сохранение рабочих весов (SQLite)
- Статистика по каждому упражнению
- Команда `/reset` — сброс текущей сессии

## Стек

- Python 3.10+
- [aiogram](https://docs.aiogram.dev/) 3.x
- SQLite

## Структура проекта

```
tg_bot_Workout/
├── bot.py                 # точка входа
├── check_bot.py           # проверка подключения к Telegram
├── config.py              # загрузка BOT_TOKEN
├── config.env.example     # шаблон конфигурации
├── requirements.txt
├── data/
│   ├── programs.json      # программы тренировок
│   └── db.sqlite          # БД (не в git, создаётся локально)
├── db/
│   └── db_helper.py       # работа с SQLite
├── handlers/
│   ├── programs.py        # выбор программы
│   ├── weights.py         # упражнения, веса, статистика
│   └── navigation.py      # переход между днями
└── scripts/
    └── backup_db.sh       # ежедневный бэкап БД
```

## Установка на Raspberry Pi

### 1. Установите системные зависимости

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

### 2. Скопируйте проект на Raspberry Pi

Если репозиторий уже есть на Raspberry Pi, перейдите в папку проекта. В противном случае передайте проект через `scp`, `rsync` или USB-накопитель.

Пример с `scp`:

```bash
scp -r user@vps:/path/to/tg_bot_Workout ~/projects/tg_bot_Workout
```

```bash
cd ~/projects/tg_bot_Workout
```

### 3. Настройте виртуальное окружение

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Создайте `config.env`

```bash
cp config.env.example config.env
nano config.env
```

Добавьте токен бота:

```env
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 5. Восстановление базы данных

Если нужно перенести данные с VPS, используйте резервную копию из `botadmin/backups/database/db_20260801_030001.sqlite` и положите её как `data/db.sqlite` в папке проекта.

```bash
cp ../../backups/database/db_20260801_030001.sqlite data/db.sqlite
```

При первом запуске, если `data/db.sqlite` отсутствует, база создаётся автоматически.

### 6. Проверка подключения к Telegram

```bash
source .venv/bin/activate
python check_bot.py
```

### 7. Запуск бота

```bash
source .venv/bin/activate
python bot.py
```

## Запуск как сервис systemd

Создайте сервис `/etc/systemd/system/tg-bot-workout.service`:

```ini
[Unit]
Description=Telegram Workout Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/projects/tg_bot_Workout
ExecStart=/home/pi/projects/tg_bot_Workout/.venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Замените `User=pi` и пути при необходимости.

```bash
sudo systemctl daemon-reload
sudo systemctl enable tg-bot-workout
sudo systemctl start tg-bot-workout
sudo systemctl status tg-bot-workout
```

Логи:

```bash
journalctl -u tg-bot-workout -f
```

## Бэкапы базы данных

Скрипт `scripts/backup_db.sh` копирует `data/db.sqlite` в `~/backups/database/` и удаляет копии старше 30 дней.

```bash
chmod +x scripts/backup_db.sh
mkdir -p ~/backups/database
./scripts/backup_db.sh
```

Переменные:

| Переменная        | По умолчанию                    |
|-------------------|---------------------------------|
| `BOT_PROJECT_DIR` | `$HOME/projects/tg_bot_Workout` |
| `BOT_BACKUP_DIR`  | `$HOME/backups/database`        |

### Cron (ежедневно в 03:00)

```cron
0 3 * * * /home/pi/projects/tg_bot_Workout/scripts/backup_db.sh
```

## Использование бота

1. `/start` — выбрать программу (Программа 1 или Программа 2)
2. После выбора программы выбрать день:
   - нажать `1-й день`, либо
   - `Выбрать день по номеру`
3. Ввести номер дня и продолжить тренировки
4. Навигация по кнопкам: `Следующее упражнение`, `Назад`, `Следующий день`, `Предыдущий день`
5. Ввести новый вес и сохранить его
6. Просмотреть статистику по упражнению
7. `/reset` — сбросить текущую сессию

## Что хранить локально

- `config.env` — токен бота
- `data/db.sqlite` — локальная база данных
- `bot.log` — локальные логи

## Миграция с VPS

1. Скопируйте резервную копию БД с VPS.
2. Поместите файл в `data/db.sqlite` в проекте.
3. Передайте `config.env` с токеном на Raspberry Pi.
4. Запустите бота на Raspberry Pi из виртуального окружения.

## Лицензия

Личный проект. Используйте и изменяйте по своему усмотрению.
