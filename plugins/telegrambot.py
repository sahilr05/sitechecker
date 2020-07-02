import jsonpickle
import telegram
from django_telegrambot.apps import DjangoTelegramBot
from telegram.ext import CommandHandler

from checkerapp.models import Profile

# from telegram.ext import Dispatcher
# from telegram.ext import Filters
# from telegram.ext import MessageHandler
# from telegram.ext import Updater

chat_ids = set()
bot_token = "***REMOVED***"
bot = telegram.Bot(token=bot_token)


def send_alert(message, user):
    bot.send_message(chat_id=user.profile.telegram_id, text=message)


def remove(update, context):
    Profile.objects.filter(telegram_id=update.message.chat_id).update(telegram_id=None)
    message = "Removing you from alerts..."
    update.message.reply_text(message)


def start(update, context):
    message = "Welcome ! I am Site Checker bot. Please enter your phone number using /register xxxxxx to proceed or /get_id to get your chat ID"
    update.message.reply_text(message)


def get_id(update, context):
    chat_id = update.message.chat_id
    message = f"Add {chat_id} in My Account > Alert Plugins > Telegram"
    update.message.reply_text(message)


def get_all_ids(update, context):
    chat_id = update.message.chat_id
    chat_ids.add(chat_id)
    update.message.reply_text(jsonpickle.encode(chat_ids))


def register(update, context):
    try:
        phone = (context.args[0],)  # converting to tuple
        if phone in list(Profile.objects.values_list("phone")):
            if Profile.objects.filter(phone=context.args[0]).update(
                telegram_id=update.message.chat_id
            ):
                message = "Number Registered !"
            else:
                print("Failed")
        else:
            message = "Number doesn't exist in check ! \nPlease ask admin to add your number for alerts"
    except Exception as e:
        print(e)
        message = (
            "Please send your number in the following syntax : /register xxxxxxxxxx"
        )

    update.message.reply_text(message)


def start_bot():
    dp = DjangoTelegramBot.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("remove", remove))
    dp.add_handler(CommandHandler("get_id", get_id))
    dp.add_handler(CommandHandler("chat_ids", get_all_ids))
    dp.add_handler(CommandHandler("register", register))


start_bot()
