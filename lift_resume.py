from playwright.sync_api import sync_playwright
from config import LOGIN, PASSWORD
from notify import send_telegram_message

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print("Step 1")
            page.goto("https://hh.ru/account/login")
            page.wait_for_timeout(2000)
            
            print("Step 2")
            submit_btn = page.locator('button[data-qa="submit-button"]')
            submit_btn.click()
            page.wait_for_timeout(2000)
            
            print("Step 3")
            page.click('text="Почта"')
            page.wait_for_timeout(2000)
            
            print("Step 4")
            page.wait_for_selector("input[name='username']", timeout=15000)
            page.fill("input[name='username']", LOGIN)  
            page.wait_for_timeout(2000)
             
            print("Step 5")
            page.wait_for_selector('text="Войти с паролем"')
            page.click('text="Войти с паролем"')   
            page.wait_for_timeout(2000)
                  
            print("Step 6")
            page.wait_for_selector("input[name='password']", timeout=15000)
            page.fill("input[name='password']", PASSWORD)
            page.wait_for_timeout(2000)
            
            print("Step 7")
            page.wait_for_selector('button[data-qa="submit-button"]', timeout=15000)
            page.click('button[data-qa="submit-button"]')
            page.wait_for_timeout(2000)
            
            print("Step 8")
            page.goto("https://hh.ru/applicant/resumes")
            page.wait_for_timeout(2000)
            
            print("Step 9")
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
