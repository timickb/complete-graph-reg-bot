import logging
import os
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from registrator import Registrator

INCORRECT_FORMAT_MESSAGE = "Некорректный формат"
SUCCESS_MESSAGE = "Визит успешно зафиксирован!"
SUCCESS_AUTH_MESSAGE = "Вы успешно авторизованы!"
NOT_AUTHORIZED_MESSAGE = "Введите корректный код доступа к системе, чтобы иметь возможность регистрировать гостей."
BOT_TOKEN = os.environ['CGRB_BOT_TOKEN']
CREDENTIALS_FILE = 'key.json'
SPREADSHEET_ID = os.environ['CGRB_SPREADSHEET_ID']
SHEET_ID = os.environ['CGRB_SHEET_ID']
TEST_SPREADSHEET_ID = os.environ['CGRB_TEST_SPREADSHEET_ID']
PASSWORD = os.environ['CGRB_PASSWORD']

registrator = Registrator(CREDENTIALS_FILE, SPREADSHEET_ID, SHEET_ID)

authorized_users = []

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def validate_name(name):
    if len(name) > 20:
        return False
    blocked = "=!@#$%^&*()\{\}'/<>[].,"
    for letter in blocked:
        if letter in name:
            return False
    return True


def start(update: Update, _: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_text('Hello!')

def register(update: Update, _: CallbackContext) -> None:
    
    if update.effective_user.id not in authorized_users:
        if update.message.text == PASSWORD:
            authorized_users.append(update.effective_user.id)
            update.message.reply_text(SUCCESS_AUTH_MESSAGE)
            return
        else:
            update.message.reply_text(NOT_AUTHORIZED_MESSAGE)
            return

    words = update.message.text.split()

    if len(words) == 2:
        name = words[0]
        tariff = words[1]      
        try:
            tariff = float(tariff)
        except ValueError:
            update.message.reply_text(INCORRECT_FORMAT_MESSAGE)
            return
        
        if not validate_name(name):
            update.message.reply_text(INCORRECT_FORMAT_MESSAGE)
            return

        registrator.register_visitor(name, '', tariff)
        update.message.reply_text(SUCCESS_MESSAGE)
        return

    if len(words) == 3:
        name = words[0]
        surname = words[1]
        tariff = words[2]
        try:
            tariff = float(tariff)
        except ValueError:
            update.message.reply_text(INCORRECT_FORMAT_MESSAGE)
            return

        if (not validate_name(name)) or (not validate_name(surname)):
            update.message.reply_text(INCORRECT_FORMAT_MESSAGE)
            return

        registrator.register_visitor(name, surname, tariff)
        update.message.reply_text(SUCCESS_MESSAGE)
        return

    update.message.reply_text(INCORRECT_FORMAT_MESSAGE)


def main():
    updater = Updater(BOT_TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, register))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
