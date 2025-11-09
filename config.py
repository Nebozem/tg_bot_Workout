import os
from dotenv import load_dotenv

load_dotenv("config.env")
BOT_TOKEN = os.getenv("BOT_TOKEN")
