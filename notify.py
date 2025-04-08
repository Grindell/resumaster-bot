import requests
from config import TOKEN, CHAT_ID

def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={'chat_id': CHAT_ID, 'text': text})
    except Exception as e:
        print(f"❌ Ошибка при отправке Telegram-сообщения: {e}")