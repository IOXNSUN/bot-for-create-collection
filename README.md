# bot-for-create-collection

## О проекте
Telegram-бот для автоматического создания Postman-коллекций.  
Позволяет тестировщикам и инженерам сопровождения быстро генерировать готовые коллекции для тестирования API платежных систем (CPA и SKIP-CPA), подставляя нужные merchant_id и account_id.

## 🚀 Возможности
- **Генерация Postman-коллекций** по шаблонам (CPA / SKIP_CPA)
- **Автоматическая подстановка** merchant_id и account_id в переменные коллекции
- **Удобный интерфейс:** inline-кнопки и пошаговый wizard
- **Безопасность:** экранирование HTML, валидация ввода, автоматическая очистка временных файлов
- **Логирование** всех действий для аудита

## 🛠 Технологии
- **Python 3.10**, asyncio
- **python-telegram-bot** (Telegram Bot API)
- **JSON** (работа с Postman-коллекциями)


## Установка и запуск

git clone https://github.com/IOXNSUN/bot-for-create-collection.git
cd bot-for-create-collection
python SKIP_CPA.py
