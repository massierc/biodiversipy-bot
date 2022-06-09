import logging
import random

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Dispatcher,
    Filters,
    MessageHandler,
    ConversationHandler,
)

from location_handler import location_handler
from utils import log_update

logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    log_update(update, logger)
    text = "\n\n".join(
        [
            f"Welcome to {context.bot.first_name}!",
            "Learn about us 👉 /about",
            "Or run one of the commands from the menu below 👇",
        ]
    )
    update.message.reply_text(text)


def about(update: Update, context: CallbackContext):
    log_update(update, logger)
    text = "\n".join(
        [
            f"🔍 {context.bot.first_name} is an AI tool developed for educational and demonstration purposes only.\n",
            "🗺️ <code>Input  </code> A location in Germany",
            "🌿 <code>Output </code> The 5 plant species most likely present at that location\n",
            "The model was trained using about 2 million observations in Germany. It makes predictions using environmental features retrieved from open-access databases:\n",
            "⛅️ Bioclimatic data, such as temperature and precipitation",
            "🪨 Soil properties, such as pH and CEC",
            "⛰️ Topographic data, such as elevation\n",
            "<i>Source code, data sources, licenses and disclaimers on https://github.com/TmtStss/biodiversipy</i>",
        ]
    )
    update.message.reply_html(text, disable_web_page_preview=True)


def bad_command(update: Update, context: CallbackContext):
    """Raise an error to trigger the error handler."""
    log_update(update, logger)
    context.bot.wrong_method_name()


def sup(update: Update, _):
    log_update(update, logger)
    replies = [
        "Molto bene 🤌",
        "Peace ✌️",
        "Life is good 🙌",
        "Hi 👋",
        "Bring it on 💪",
        "Yo 🤙",
    ]
    text = "\n\n".join([random.choice(replies), "Are you looking for /find ?"])
    update.message.reply_text(text)


def unknown(update: Update, _):
    log_update(update, logger)
    text = "\n\n".join(
        ["Sorry, I didn't get it. I'm a simple bot 🙈", "Are you looking for 👉 /find ?"]
    )
    update.message.reply_text(text)


def error_handler(update: Update, context: CallbackContext):
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    update.message.reply_text("Sorry, an error occurred. Try again!")

    return ConversationHandler.END


def remove_keyboard(update: Update, _):
    log_update(update, logger)
    update.message.reply_text("Done!", reply_markup=ReplyKeyboardRemove())


command_handlers = [
    ("start", start),
    ("about", about),
    ("kaboom", bad_command),
]

message_handlers = [
    (sup, Filters.regex(f"^(?i)(yo|sup|hey|hi|hello|what's up|what up|whatsup).*$")),
    (remove_keyboard, Filters.regex(f"^(?i)(remove keyboard|rmkb)$")),
    (unknown, Filters.text & (~Filters.command)),
]


def register_handlers(dispatcher: Dispatcher):
    for (id, fn) in command_handlers:
        dispatcher.add_handler(CommandHandler(id, fn))

    dispatcher.add_handler(location_handler)

    for (fn, filters) in message_handlers:
        dispatcher.add_handler(MessageHandler(filters, fn))

    dispatcher.add_error_handler(error_handler)
