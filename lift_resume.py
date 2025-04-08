from playwright.sync_api import sync_playwright
from config import LOGIN, PASSWORD
from notify import send_telegram_message

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Step 1
            page.goto("https://hh.ru/account/login", timeout=30000)
            # Step 2
            page.wait_for_selector("input[name='login']", timeout=15000)
            page.fill("input[name='login']", LOGIN)            
            # Step 3
            page.locator("a[data-qa='expand-login-by-password']").click(force=True)
            page.wait_for_timeout(2000)
            # Step 4
            page.wait_for_selector("input[name='password']:not([type='hidden'])", timeout=15000)
            page.fill("input[name='password']:not([type='hidden'])", PASSWORD)
            # Step 5
            page.locator("text='Войти в личный кабинет'").click()
            page.wait_for_timeout(3000)
            # Step 6
            page.goto("https://hh.ru/applicant/resumes")
            page.wait_for_timeout(2000)
            # Step 7
            lift_button = page.locator("button:has-text('Поднять')")
            if lift_button.count() > 0:
                lift_button.first.click()
                send_telegram_message("✅ Резюме успешно поднято.")
            else:
                send_telegram_message("⚠️ Кнопка 'Поднять' не найдена.")

        except Exception as e:
            send_telegram_message(f"❌ Ошибка при поднятии:\n{e}")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
