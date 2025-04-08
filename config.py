import os
from dotenv import load_dotenv
load_dotenv()

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")