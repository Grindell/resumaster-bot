# main.py

import schedule
import time
from lift_resume import run as lift_resume
from check_views import run as check_views
from notify import send_telegram_message
import logging

logging.basicConfig(level=logging.INFO)

def job_lift_resume():
    try:
        logging.info("🔁 Запуск задачи поднятия резюме...")
        lift_resume()
    except Exception as e:
        send_telegram_message(f"❌ Ошибка при запуске задачи поднятия резюме:\n{e}")
        logging.error(f"❌ Ошибка при запуске задачи поднятия резюме:\n{e}")

def job_check_views():
    try:
        logging.info("🔁 Запуск задачи парсинга просмотров...")
        check_views()
    except Exception as e:
        send_telegram_message(f"❌ Ошибка при запуске задачи парсинга просмотров:\n{e}")
        logging.error(f"❌ Ошибка при запуске задачи парсинга просмотров:\n{e}")

# Планирование задач
schedule.every(4).hours.do(job_lift_resume)  # Поднятие резюме раз в 4 часа
schedule.every(30).minutes.do(job_check_views)  # Парсинг просмотров раз в 30 минут

logging.info("📅 Планировщик запущен. Поднятие резюме каждые 4 часа, парсинг просмотров каждые 30 минут...")

while True:
    schedule.run_pending()
    time.sleep(1)
