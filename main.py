# main.py

import schedule
import time
import json
from lift_resume import run as lift_resume
from notify import send_telegram_message
import logging

logging.basicConfig(level=logging.INFO)

def load_schedule():
    with open("schedule.json", "r", encoding="utf-8") as f:
        return json.load(f)

def job_lift_resume():
    try:
        logging.info("🔁 Запуск задачи поднятия резюме...")
        lift_resume()
    except Exception as e:
        send_telegram_message(f"❌ Ошибка при поднятии резюме:\n{e}")
        logging.error(f"❌ Ошибка при поднятии резюме:\n{e}")

def setup_schedule():
    config = load_schedule()
    lift_times = config.get("lift_resume_times", [])

    for t in lift_times:
        schedule.every().day.at(t).do(job_lift_resume)
        logging.info(f"📌 Поднятие резюме запланировано на {t}")

if __name__ == "__main__":
    setup_schedule()
    logging.info("📅 Планировщик запущен...")

    while True:
        schedule.run_pending()
        time.sleep(1)
