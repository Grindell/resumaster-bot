# main.py

import schedule
import time
import json
from lift_resume import run as lift_resume
from check_views import run as check_views
from notify import send_telegram_message
import logging

logging.basicConfig(level=logging.INFO)

# Загрузка расписания из файла
def load_schedule():
    with open("schedule.json", "r", encoding="utf-8") as f:
        return json.load(f)

# Задачи
def job_lift_resume():
    try:
        logging.info("🔁 Запуск задачи поднятия резюме...")
        lift_resume()
    except Exception as e:
        send_telegram_message(f"❌ Ошибка при поднятии резюме:\n{e}")
        logging.error(f"❌ Ошибка при поднятии резюме:\n{e}")

def job_check_views():
    try:
        logging.info("🔁 Запуск задачи парсинга просмотров...")
        check_views()
    except Exception as e:
        send_telegram_message(f"❌ Ошибка при парсинге просмотров:\n{e}")
        logging.error(f"❌ Ошибка при парсинге просмотров:\n{e}")

# Установка расписания
def setup_schedule():
    config = load_schedule()
    lift_times = config.get("lift_resume_times", [])
    check_times = config.get("check_views_times", [])

    for t in lift_times:
        schedule.every().day.at(t).do(job_lift_resume)
        logging.info(f"📌 Поднятие резюме запланировано на {t}")

    for t in check_times:
        schedule.every().day.at(t).do(job_check_views)
        logging.info(f"📌 Парсинг просмотров запланирован на {t}")

# Точка входа
if __name__ == "__main__":
    setup_schedule()
    logging.info("📅 Планировщик запущен...")

    while True:
        schedule.run_pending()
        time.sleep(1)
