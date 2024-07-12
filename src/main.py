import logging
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext
from googleapiclient.discovery import build
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta

logging.basicConfig(level=logging.DEBUG)

# Токен вашего телеграм-бота
TELEGRAM_TOKEN = '**********JBMX6*****'

# Путь к файлу с учетными данными Google Sheets и идентификатор таблицы
CREDS_JSON_PATH = r"data_json.json"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = '**********JBMX6*****'

# Инициализация телеграм-бота
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
bot = updater.bot

# Инициализация сервиса Google Sheets
creds_service = ServiceAccountCredentials.from_json_keyfile_name(CREDS_JSON_PATH, SCOPES).authorize(httplib2.Http())
sheets_service = build('sheets', 'v4', http=creds_service)
sheet = sheets_service.spreadsheets()

# Обработка команды /start
def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("/info")],
        [KeyboardButton("/record")],
        [KeyboardButton("/google_sheet")],
        [KeyboardButton("/google_last_comment")],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    start_text = ("Привет! Я бот для добавления данных в Google Sheets. \n"
                  "Я как бот буду помогать вам контролировать Диабет для дальнейшего анализа врачом.")
    update.message.reply_text(start_text, reply_markup=reply_markup)

def info(update: Update, context: CallbackContext) -> None:
    info_text = ("Привет! Я бот для добавления данных в Google Sheets.\n"
                 "Вот что я умею: \n"
                 "/start - Начало взаимодействия с ботом \n"
                 "/info - Информация о боте \n"
                 "/record - Команда для записи данных в бота \n"
                 "Пример заноса данных: \n"
                 "/record Лист1 12.01.2023 21:00 день 7.3 Съел печенье \n"
                 "Ответ: \n"
                 "Данные добавлены в лист Лист1.\n"
                 "/google_sheet - команда для получения ссылки для гугл таблицы. \n"
                 "/google_last_comment - команда для получения внесения последней записи")
    update.message.reply_text(info_text)

def google_sheet(update: Update, context: CallbackContext) -> None:
    sheet_id_s = 'id_sheet'
    sheet_link = f'https://docs.google.com/spreadsheets/d/{sheet_id_s}'
    info_google = (f"Вот таблица с вашими данными: {sheet_link}")
    update.message.reply_text(info_google)

def get_last_entry() -> dict:
    sheet_id = 'id_sheet'  # Замените на ваш идентификатор таблицы
    sheet_range = 'Лист1!A:F'  # Замените на ваш диапазон столбцов

    response = sheet.values().get(spreadsheetId=sheet_id, range=sheet_range).execute()
    values = response.get('values', [])
    if values:
        last_entry = values[-1]
        return {
            'date': last_entry[0],
            'time': last_entry[1],
            'time_desc': last_entry[2],
            'value': last_entry[3],
            'comment': last_entry[4],
        }
    else:
        return {}

def google_last_comment(update: Update, context: CallbackContext) -> None:
    sheet_name = "Лист1"
    sheet_range = f"{sheet_name}!A:F"
    last_entry = get_last_entry()

    if last_entry:
        last_entry_text = (
            f"Последняя добавленная запись:\n"
            f"Дата: {last_entry['date']}\n"
            f"Время: {last_entry['time']}\n"
            f"Время (описание): {last_entry['time_desc']}\n"
            f"Сахар: {last_entry['value']}\n"
            f"Комментарии: {last_entry['comment']}"
        )
    else:
        last_entry_text = "В таблице нет записей."

    update.message.reply_text(last_entry_text)

def remind_user(context: CallbackContext):
    user_id = context.job.context['user_id']
    context.bot.send_message(chat_id=user_id, text="Пора проверить уровень сахара!")

def record(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_data = context.user_data

    text = update.message.text
    match = re.match(r'/record (\S+) (\S+ \S+) (\S+) (\S+) (.+)', text)

    try:
        if match:
            sheet_name, timestamp, time_desc, value, comment = match.groups()

            # Получение указанного листа
            sheet_instance = sheet.get(spreadsheetId=SHEET_ID).execute()
            sheet_id = sheet_instance['sheets'][0]['properties']['sheetId']
            sheet_range = f"{sheet_name}!A1:F"

            date, time = timestamp.split(' ', 1)  # Разделяем timestamp только на две части

            # Добавление данных в таблицу
            sheets_service.spreadsheets().values().append(
                spreadsheetId=SHEET_ID,
                range=sheet_range,
                body={'values': [[date, time, time_desc, value, comment, '']]},  # Добавлен пустой столбец
                valueInputOption='RAW'  # Добавлен параметр valueInputOption
            ).execute()

            update.message.reply_text(f'Данные добавлены в лист {sheet_name}.')
        else:
            raise ValueError('Invalid command format')

    except Exception as e:
        update.message.reply_text(f'Ошибка при добавлении данных: {str(e)}')

    job_queue = context.job_queue
    alarm_time_value, user_id_value = alarm_time(update)
    job_queue.run_once(remind_user, timedelta(hours=1), context={'user_id': user_id_value})

def alarm_time(update: Update) -> datetime:
    user_id_value = update.message.from_user.id
    return datetime.now().replace(hour=21, minute=50, second=0, microsecond=0), user_id_value

def send_alarm(context: CallbackContext):
    try:
        user_id = context.job.context['user_id']
        context.bot.send_message(chat_id=user_id, text="Уже скоро 10 часов. Необходимо сделать ночной инсулин!")
    except Exception as e:
        print(f"Error in send_alarm: {e}")

if __name__ == "__main__":
    # Добавление обработчиков в диспетчер
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("record", record))
    updater.dispatcher.add_handler(CommandHandler("info", info))
    updater.dispatcher.add_handler(CommandHandler("google_sheet", google_sheet))
    updater.dispatcher.add_handler(CommandHandler("google_last_comment", google_last_comment))

    # Запуск бота
    updater.start_polling()
    updater.idle()
