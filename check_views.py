import logging
import os
from playwright.sync_api import sync_playwright
from config import LOGIN, PASSWORD
from notify import send_telegram_message
from datetime import datetime
import re
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Путь к файлу для хранения просмотренных компаний
VIEWS_LOG_FILE = "views_log.json"

def load_views_log():
    if os.path.exists(VIEWS_LOG_FILE):
        try:
            with open(VIEWS_LOG_FILE, "r", encoding="utf-8") as file:
                # Проверяем, что файл не пуст и можно загрузить данные
                data = file.read().strip()
                if not data:  # Если файл пуст
                    return {}
                return json.loads(data)
        except json.JSONDecodeError as e:
            logging.error(f"❌ Ошибка при чтении JSON: {e}")
            return {}  # Возвращаем пустой словарь, если ошибка чтения
    return {}

def save_views_log(views):
    try:
        with open(VIEWS_LOG_FILE, "w", encoding="utf-8") as file:
            json.dump(views, file, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"❌ Ошибка при сохранении JSON: {e}")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Показываем браузер для отладки
        page = browser.new_page()

        try:
            # Step 1
            logging.info("🌐 Переход на страницу логина...")
            page.goto("https://hh.ru/account/login", timeout=30000)
            # Step 2
            logging.info("📥 Ожидаем поле для ввода логина...")
            page.wait_for_selector("input[name='login']", timeout=15000)
            page.fill("input[name='login']", LOGIN)            
            logging.info("📥 Логин введен.")
            # Step 3
            logging.info("📥 Кликаем на 'Войти с паролем'...")
            page.locator("a[data-qa='expand-login-by-password']").click(force=True)
            page.wait_for_timeout(2000)
            logging.info("🔑 Поле для пароля открыто.")
            # Step 4
            logging.info("🔑 Ожидаем поле для ввода пароля...")
            page.wait_for_selector("input[name='password']:not([type='hidden'])", timeout=15000)
            page.fill("input[name='password']:not([type='hidden'])", PASSWORD)
            logging.info("🔑 Пароль введен.")
            # Step 5
            logging.info("📥 Кликаем по кнопке 'Войти в личный кабинет'...")
            page.locator("text='Войти в личный кабинет'").click()
            page.wait_for_timeout(3000)
            logging.info("✅ Вход выполнен.")
            # Step 6
            logging.info("📄 Переход к резюме...")
            page.goto("https://hh.ru/applicant/resumes")
            page.wait_for_timeout(2000)
            logging.info("📄 Страница резюме загружена.")
            # Step 7: Клик по просмотрам
            logging.info("🔍 Ищем ссылку на просмотры...")
            views_link = page.locator("a[data-qa='count-new-views']")
            if views_link.count() == 0:
                send_telegram_message("⚠️ Ссылка на просмотры не найдена.")
                logging.warning("⚠️ Ссылка на просмотры не найдена.")
                return

            views_link.first.click()
            page.wait_for_timeout(2000)
            logging.info("🔍 Открыта история просмотров.")

            # Step 8: Парсинг просмотров
            logging.info("🔍 Сбор данных о просмотрах...")
            company_blocks = page.locator("div[data-qa^='resume-view-history-table-company-']")
            views = []

            # Загружаем ранее просмотренные компании
            viewed_companies = load_views_log()

            for i in range(company_blocks.count()):
                block = company_blocks.nth(i)
                try:
                    # Название компании
                    company_name_el = block.locator("[data-qa='link-text']")
                    if company_name_el.count() > 0:
                        company = company_name_el.inner_text().strip().strip(",")
                    else:
                        logging.warning(f"⚠️ У блока {i} не найден элемент 'link-text'")
                        continue

                    logging.info(f"Компания: {company}")

                    # Пропуск, если уже была
                    if company in viewed_companies:
                        logging.info(f"Компания {company} уже была проверена.")
                        continue

                    # Кол-во просмотров
                    views_text_el = block.locator("[data-qa='resume-view-history-table-company-views-link-text']")
                    if views_text_el.count() > 0:
                        views_text = views_text_el.inner_text()
                        match = re.search(r"(\d+)", views_text)
                        views_count = int(match.group(1)) if match else 1
                    else:
                        logging.warning(f"⚠️ Не найден блок с количеством просмотров у компании {company}, ставим 1 просмотр.")
                        views_count = 1

                    # Время просмотра (ищем вручную среди div)
                    view_time = None
                    try:
                        all_divs = block.locator("div")
                        for k in range(all_divs.count()):
                            candidate = all_divs.nth(k)
                            candidate_text = candidate.inner_text().strip()
                            if re.match(r"\d{2}:\d{2}", candidate_text):
                                view_time = candidate_text
                                break
                        logging.info(f"Время просмотра: {view_time}")
                    except Exception as e:
                        logging.warning(f"⚠️ Не удалось получить время просмотра для {company}: {e}")
                        view_time = None

                    # Добавляем компанию в список
                    views.append(f"{company} — {views_count} просмотров {view_time or ''}")
                    viewed_companies[company] = {"views_count": views_count, "view_time": view_time}

                except Exception as e:
                    logging.error(f"Ошибка при парсинге для компании {i}: {e}")
                    continue


            # Сохраняем данные о просмотренных компаниях
            save_views_log(viewed_companies)

            # Логируем итог
            if views:
                message = "📊 Просмотры резюме:\n" + "\n".join(views)
                send_telegram_message(message)
                logging.info("📊 Просмотры успешно отправлены в Telegram.")
            else:
                send_telegram_message("🔕 Просмотры не найдены.")
                logging.info("🔕 Просмотры не найдены.")

        except Exception as e:
            send_telegram_message(f"❌ Ошибка при проверке просмотров:\n{e}")
            logging.error(f"❌ Ошибка при проверке просмотров:\n{e}")
        finally:
            logging.info("🧹 Закрытие браузера...")
            browser.close()

def parse_russian_date(text: str) -> datetime:
    months = {
        "января": 1, "февраля": 2, "марта": 3, "апреля": 4,
        "мая": 5, "июня": 6, "июля": 7, "августа": 8,
        "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
    }
    parts = text.lower().split()
    return datetime(datetime.now().year, months.get(parts[1], 1), int(parts[0]))

if __name__ == "__main__":
    run()
