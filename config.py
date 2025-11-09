from dotenv import load_dotenv
import os

env_path = os.path.join(os.path.dirname(__file__), "config.env")
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
print("BOT_TOKEN:", BOT_TOKEN)