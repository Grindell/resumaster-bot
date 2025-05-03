# main.py

import schedule
import time
import logging
import json
import requests
from playwright.sync_api import sync_playwright
# ————————————————————————————————
# Telegram-настройки
TG_BOT_TOKEN = "7584007399:AAHAq4Aoa6hYk0BipXuBHNzflGStld2LzCU"
TG_CHAT_ID   = "1872573324"

def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": TG_CHAT_ID, "text": text}, timeout=5)
    except Exception as e:
        logging.error(f"Не удалось отправить ТГ: {e}")

# ————————————————————————————————
# Время для поднятия (HH:MM)
LIFT_TIMES = ["05:55", "10:00", "14:05", "14:50", "18:10"]

logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

def job_lift_resume(page):
    """Кликаем «Поднять» на странице резюме."""
    try:
        logging.info("🔁 Поднимаем резюме…")
        # просто обновляем страницу
        page.goto("https://hh.ru/applicant/resumes")
        page.wait_for_timeout(2000)

        btns = page.locator("button:has-text('Поднять')")
        if btns.count() > 0:
            btns.first.click()
            logging.info("✅ Резюме поднято")
            send_telegram_message("✅ Резюме успешно поднято.")
        else:
            logging.warning("⚠️ Кнопка 'Поднять' не найдена")
            send_telegram_message("⚠️ Кнопка 'Поднять' не найдена.")
    except Exception as e:
        logging.exception("❌ Ошибка при поднятии резюме")
        send_telegram_message(f"❌ Ошибка при поднятии:\n{e}")

def main():
    # 1) Запускаем Playwright
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # 2) Открываем страницу логина и ждём, пока вы вручную залогинитесь и решите капчу
    page.goto("https://hh.ru/account/login")
    print("\n➡️ Откройте в браузере логин-форму, введите логин/пароль, решите капчу.")
    print("   После успешного входа перейдите на страницу резюме и дождитесь продолжения…\n")
    page.wait_for_url("https://hh.ru/applicant/resumes", timeout=0)

    # 3) Сохраняем текущее состояние (куки+localStorage) в переменную
    storage_state: dict = context.storage_state()
    logging.info("💾 Сессия сохранена в переменной storage_state")

    # (По желанию) можно перебросить это состояние в новый контекст:
    # context.close()
    # context = browser.new_context(storage_state=storage_state)
    # page = context.new_page()

    # 4) Настраиваем планировщик
    for t in LIFT_TIMES:
        schedule.every().day.at(t).do(job_lift_resume, page)
        logging.info(f"📌 Запланировано поднятие резюме в {t}")

    logging.info("📅 Планировщик запущен — ждём своего времени…")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    finally:
        context.close()
        browser.close()
        pw.stop()

if __name__ == "__main__":
    main()
