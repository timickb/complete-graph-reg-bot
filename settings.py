import os

# Строковые ресурсы.
INCORRECT_FORMAT_MESSAGE = "Некорректный формат. Правильно так: <Имя> <Фамилия> <Тариф> [Комментарий]"
INCORRECT_RECEIPT_FORMAT_MESSAGE = "Необходимо указать корректный (= целочисленный) идентификатор посетителя, которого хотите рассчитать."
UNKNOWN_VISIT_ID_MESSAGE = "Посетитель с таким идентификатором не найден."
SUCCESS_MESSAGE = "Визит успешно зафиксирован! Идентификатор посетителя - "
SUCCESS_AUTH_MESSAGE = "Вы успешно авторизованы!"
NOT_AUTHORIZED_MESSAGE = "Введите корректный код доступа к системе, чтобы иметь возможность регистрировать гостей."
FIRST_USE_MESSAGE = "Вижу, ты здесь впервые. Отправь мне, пожалуйста, парольчик."
HELLO_MESSAGE = "Привет! С возвращением!"
RECEIPT_MESSAGE = "Посетитель %s провел(а) в заведении %s времени и обязан(а) заплатить %s рублей."

# Авторизационные данные.
BOT_TOKEN = os.environ['CGRB_BOT_TOKEN']
TEST_BOT_TOKEN = os.environ['CGRB_TEST_BOT_TOKEN']
CREDENTIALS_FILE = 'key.json'
SPREADSHEET_ID = os.environ['CGRB_SPREADSHEET_ID']
SHEET_ID = os.environ['CGRB_SHEET_ID']
TEST_SHEET_ID = 0
TEST_SPREADSHEET_ID = os.environ['CGRB_TEST_SPREADSHEET_ID']
PASSWORD = os.environ['CGRB_PASSWORD']

# Структура таблицы.
VISITOR_NAME_COLUMN_ID = 1
VISITOR_ARRIVE_COLUMN_ID = 2
VISITOR_TARIFF_COLUMN_ID = 3
VISITOR_DEPARTURE_COLUMN_ID = 4
TIME_FORMULA_COLUMN_ID = 5
RECEIPT_FORMULA_COLUMN_ID = 6
COMMENT_COLUMN_ID = 7

# Ограничения.
BLOCKED_NAME_SYMBOLS = "=!@#$%^&*\{\}'/<>[].,"
MAX_NAME_LENGTH = 20
MAX_TARIFF_VALUE = 8

# Команды
RECEIPT_COMMAND = "чек"