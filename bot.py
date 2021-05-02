import logging
import os
import sys
import settings
import json

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from registrator import Registrator


def validate_name(name):

    if len(name) > settings.MAX_NAME_LENGTH:
        return False

    for letter in settings.BLOCKED_NAME_SYMBOLS:
        if letter in name:
            return False
    return True


def validate_tariff(tariff):
    try:
        tariff = float(tariff)
    except ValueError:
        return False
    return (tariff >= 0) and (tariff <= settings.MAX_TARIFF_VALUE)


def authorize_user(user_id, password):
    if password == settings.PASSWORD:
        authorized_users.append(user_id)
        with open("authorized_users.json", "w") as f:
            f.write(json.dumps(authorized_users))
        return True
    return False


def start_handler(update: Update, _: CallbackContext) -> None:
    if update.effective_user.id in authorized_users:
        update.message.reply_text(settings.HELLO_MESSAGE)
        return
    update.message.reply_text(settings.FIRST_USE_MESSAGE)


def message_handler(update: Update, _: CallbackContext) -> None:
    
    if update.effective_user.id not in authorized_users:
        if authorize_user(update.effective_user.id, update.message.text):
            update.message.reply_text(settings.SUCCESS_AUTH_MESSAGE)
            return
        else:
            update.message.reply_text(settings.NOT_AUTHORIZED_MESSAGE)
            return

    words = update.message.text.split()
    name = surname = tariff = None

    if len(words) == 2:
        name = words[0]
        surname = ''
        tariff = words[1].replace(",", ".")
    elif len(words) == 3:
        name = words[0]
        surname = words[1]
        tariff = words[2].replace(",", ".")
    else:
        update.message.reply_text(settings.INCORRECT_FORMAT_MESSAGE)
        return 
        
    if (not validate_name(name)) or (not validate_name(surname)) or (not validate_tariff(tariff)):
        update.message.reply_text(settings.INCORRECT_FORMAT_MESSAGE)
        return

    registrator.register_visitor(name, surname, tariff)
    update.message.reply_text(settings.SUCCESS_MESSAGE)


def load_authorized_users():
    try:
        with open('authorized_users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def main(test=False):
    global registrator
    global authorized_users

    if test:
        registrator = Registrator(settings.CREDENTIALS_FILE, settings.SPREADSHEET_ID, settings.SHEET_ID)
    else:
        registrator = Registrator(settings.CREDENTIALS_FILE, settings.TEST_SPREADSHEET_ID, settings.TEST_SHEET_ID)

    authorized_users = load_authorized_users()

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    if test:
        updater = Updater(settings.TEST_BOT_TOKEN)
    else:
        updater = Updater(settings.BOT_TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start_handler))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    updater.start_polling()
    updater.idle()



if __name__ == "__main__":
    if len(sys.argv) > 1 and (sys.argv[1] == "--test"):
        main(test=True)
    else:
        main()
