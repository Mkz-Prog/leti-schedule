import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from asyncio import queue

my_queue = queue.Queue()

# Конфигурация
TOKEN = os.getenv("TOKEN")  # Замените на ваш токен из BotFather
URL = 'https://digital.etu.ru/schedule/?faculty=ФКТИ&schedule=group&course=1&group=4344'

def get_schedule():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем таблицу расписания (измените селекторы, если структура HTML отличается)
        table = soup.find('table', {'class': 'schedule-table'})  # Пример селектора
        
        if not table:
            return "Таблица расписания не найдена."

        # Парсим таблицу (пример обработки)
        schedule = []
        rows = table.find_all('tr')
        for row in rows[1:]:  # Пропускаем заголовок
            cols = row.find_all('td')
            time = cols[0].text.strip()
            subject = cols[1].text.strip() if len(cols) > 1 else ''
            schedule.append(f"{time}: {subject}")
        
        return "\n".join(schedule) if schedule else "Расписание пустое."

    except Exception as e:
        return f"Ошибка: {str(e)}"

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Привет! Отправьте /schedule, чтобы получить расписание.")

def schedule(update: Update, context: CallbackContext) -> None:
    schedule_text = get_schedule()
    update.message.reply_text(f"Расписание:\n\n{schedule_text}", parse_mode='Markdown')

def main():
    # Исправленная инициализация Updater
    updater = Updater(TOKEN, update_queue=my_queue)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("schedule", schedule))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
