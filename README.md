# Telegram_bot_test

Бот с поддержкой multiple payment methods и панелью администратора.

## Функциональность

- 💳 Оплата через Telegram Stars
- 💵 Оплата рублями (Paymaster)
- ₿ Оплата криптовалютой (CryptoBot)
- 👥 Панель администратора
- 📊 Статистика и управление пользователями
- ✉️ Рассылка сообщений

## Установка

1. Клонировать репозиторий
2. Установить зависимости: `pip install -r requirements.txt`
3. Настроить `.env` файл
4. Запустить: `python bot/main.py`

## Настройка .env

```env
BOT_TOKEN=your_bot_token
ADMIN_IDS=123456789
PAYMASTER_PROVIDER_TOKEN=your_token
CRYPTOBOT_API_TOKEN=your_token
