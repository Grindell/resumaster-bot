# 🤖 Resumaster Bot

Бот на Python + Playwright, который:

- 🔁 автоматически поднимает резюме на hh.ru
- 👀 парсит просмотры резюме каждые 30 минут
- 📬 отправляет уведомления в Telegram
- 🐳 работает в Docker и запускается как фоновый процесс

---

## 📦 Установка

1. Клонируй репозиторий:

```bash
git clone https://github.com/Grindell/resumaster-bot.git
```
```bash
cd resumaster-bot
```
2 Переименуй .env.example в .env
Добавь свои данные для
```
LOGIN = example@mail.com
PASSWORD = yourpassword
TOKEN = your_bot_token
CHAT_ID = 123456789
```
🐳 Команды Makefile
        Описание
```
make build	Собрать Docker-контейнер
make up	        Запустить в фоне (демон)
make down	Остановить и удалить контейнер
make logs	Просмотр логов в реальном времени
make restart	Перезапустить контейнер
make bash	Войти внутрь контейнера
```
