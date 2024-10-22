# Разработка бота для контроля диабета
Вообще данный бот задумывался как бот, который будет использоваться на постоянной основе,который приучит к тому, чтобы заносил информацию о приеме пищи или заносил информацию о том, что необходимо сделать иекцию на основе занесенных данных , то есть если на момент заноса данных сахар слишком высокий или необходима подколка. То есть чтобы вся математика происходила без моего участия, то есть один раз правильно посчитал, а дальше ввел формулу и он сам.

## Разработка бота
Разрботка сама заняла не так много времени, так как документация у API довольно понятна и нет большой сложности в тестировании на питоне.
Больше всего сложности было в настройке и получении ключа API для Google Sheets, так как требовалось сделать пользователя , который сможет заносить информацию без основого пользователя. А Google постоянно просходит обновление , и просто при просмотре видео, получается так, что просто автор видео рассказывает о методе, который уже устарел.


## Описание Импортов в Python-Telegram-Bot

### Update

Этот импорт предоставляет класс `Update`, который используется для представления объектов обновлений (`updates`) от Telegram.

Обновления представляют собой события, происходящие в чате, например, когда кто-то отправляет сообщение вашему боту.

### Updater

Этот импорт предоставляет класс `Updater`, который является основным компонентом для взаимодействия с API Telegram. 

Он автоматически получает обновления от Telegram и передает их обработчикам.

### CommandHandler

Этот импорт предоставляет класс `CommandHandler`, который используется для создания обработчиков команд.

Обработчики команд вызываются, когда пользователь отправляет определенную команду боту, например, `/start` или `/help`.

### MessageHandler, Filters

Этот импорт предоставляет класс `MessageHandler` для создания обработчиков сообщений. 

`Filters` используется для определения условий фильтрации сообщений, например, текстовые сообщения, изображения и так далее.

### CallbackContext 

Этот импорт предоставляет класс `CallbackContext`, который предоставляет контекст для обратных вызовов обработчиков.

Контекст содержит различные полезные объекты, такие как объект обновления (`update`), объект контекста (`context`), пользовательские данные и так далее.


### build

Этот импорт используется для создания объекта `build`, который предоставляет доступ к конкретным API Google.


### re

Этот импорт используется для вызова библиотеки для регулярного выражения для обработки и разбиения данных.

### httplib2 

Эта библиотека предоставляет функциональность для отправки HTTP-запросов. 

### ServiceAccountCredentials

Этот импорт используется для работы с учетными данными служебного аккаунта (Service Account) Google. 

Служебный аккаунт используется для авторизации доступа к Google Sheets API от имени вашего приложения.

### datetime

Этот импорт используется для работы с датами и временем. 

В данном случае, вероятно, вы будете использовать объект `datetime` для форматирования временных меток, которые вы можете добавлять в вашу таблицу.

Вместе эти импорты обеспечивают основу для создания и обработки ботов в Telegram на языке Python с использованием библиотеки `python-telegram-bot`.

`logging.basicConfig(level=logging.DEBUG)` - помогает выполнять проверку работы бота телеграмм в real-time

`TELEGRAM_TOKEN = 'токен'`- ввод токена для подключения в телеграмм

## Инструкция по работе и запуску кода бота

### Путь к файлу с учетными данными Google Sheets и идентификатор таблицы

`CREDS_JSON_PATH = r"путь\к\json-файлу\для\подключения\к\Google\Sheet"`

`SCOPES = ['https://www.googleapis.com/auth/spreadsheets']` - cсылка на гугл таблицу

`SHEET_ID = 'id_таблицы'` - id_таблицы для подключения

### Инициализация телеграм-бота

`updater = Updater(token=TELEGRAM_TOKEN, use_context=True)`- Вызов класса для работы с основными компонентами API Telegram

`bot = updater.bot`- подключение бота

### Инициализация сервиса Google Sheets

`creds_service = ServiceAccountCredentials.from_json_keyfile_name(CREDS_JSON_PATH, SCOPES).authorize(httplib2.Http())` - инициализация авторизации подключения к Google сервисам

`sheets_service = build('sheets', 'v4', http=creds_service)` - указание версиии для подключения к гуглу

`sheet = sheets_service.spreadsheets()` - подключение

### Обработка команды `/start`

`def start(update: Update, context: CallbackContext) -> None:` - создании функции для работы команды `\start`

`    update.message.reply_text('Привет! Я бот для добавления данных в Google Sheets.')` - при вводе пользователем `\start` выводится заданный текст

### Обработка команды `/record`

`def record(update: Update, context: CallbackContext) -> None:` - инициализация создания команды record

`user_id = update.message.from_user.id` - сообщение от пользователя

`user_data = context.user_data` - инициализация хранения словаря

`user_id = update.message.from_user.id`:

`update.message.from_user` - это объект, предоставляемый библиотекой python-telegram-bot, представляющий пользователя, отправившего сообщение.

`update.message.from_user.id` - получает идентификатор пользователя (ID) из объекта пользователя. Этот ID уникален для каждого пользователя и используется для идентификации.

`user_data = context.user_data`:

`context.user_data` - это словарь, предоставляемый библиотекой python-telegram-bot, который предназначен для хранения пользовательских данных между различными вызовами функций.

В данном контексте, это может быть использовано для сохранения каких-то данных о пользователе в течение сессии работы с ботом.

`text = update.message.text`- обработка сообщения от пользователя

`match = re.match(r'/record (\S+) (\S+ \S+) (\S+) (\S+) (.+)', text)`- регулярное выражение для обработки сообщения в Гугл тетрадку


### Получение данных из регулярного выражения:

`if match`:

`    sheet_name, timestamp, time_desc, value, comment = match.groups()` - Если совпадение найдено, извлекаются группы данных из регулярного выражения. `match.groups()` возвращает кортеж с данными из групп.

### Получение указанного листа в Google Sheets:

`sheet_instance = sheet.get(spreadsheetId=SHEET_ID).execute()`

`sheet_id = sheet_instance['sheets'][0]['properties']['sheetId']`

`sheet_range = f"{sheet_name}!A1:F"`

`sheet.get` - используется для получения информации о листах в Google Sheets.

`sheet_instance['sheets'][0]['properties']['sheetId']` - получает идентификатор первого листа (в данном случае, используется 0-й индекс).

`sheet_range` - формирует диапазон вида `Лист1!A1:F` на основе имени листа.

### Разделение метки времени на дату и время:

`date, time = timestamp.split(' ', 1)` - `timestamp` представляет собой строку с датой и временем. `split(' ', 1)` разделяет строку только на две части - дату и время.

### Добавление данных в таблицу Google Sheets:

`sheets_service.spreadsheets().values().append(` - `sheets_service.spreadsheets().values().append` - добавляет новую строку в таблицу.

`    spreadsheetId=SHEET_ID,`

`    range=sheet_range,`

`    body={'values': [[date, time, time_desc, value, comment, '']]},  # Добавлен пустой столбец` - данные для добавления.

`    valueInputOption='RAW'  # Добавлен параметр valueInputOption` - указывает, что данные представляют собой неформатированные значения.

`).execute()`

### Ответ пользователю о добавлении данных:

`update.message.reply_text(f'Данные добавлены в лист {sheet_name}.')` - Отправляет ответ пользователю о том, что данные успешно добавлены.

Обработчики команд `/start` и обычных текстовых сообщений также добавлены в диспетчер, а затем запускается бот с использованием `updater.start_polling()` и `updater.idle()`.
