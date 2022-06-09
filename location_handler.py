import logging

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    ConversationHandler,
)

from utils import get_coords, args_to_location
from predictor import execute_prediction

logger = logging.getLogger(__name__)


LOCATION = range(1)
LOCATION_KEYBOARD = ["Choose on map", "Send via text"]


def find(update: Update, context: CallbackContext) -> int:
    if len(context.args) == 0:
        text = "\n\n".join(
            [
                "Where should I look?",
                "You can send me a location 📍 or type an address ✍️",
            ]
        )
        update.message.reply_text(text)

        return LOCATION
    else:
        raw_location = args_to_location(context.args)
        coords = get_coords(raw_location, update)
        return execute_prediction(coords, update)


def location(update: Update, _) -> int:
    user_location = update.message.location
    user_text = update.message.text

    if user_location:
        coords = (user_location.latitude, user_location.longitude)
        return execute_prediction(coords, update)
    elif user_text:
        coords = get_coords(user_text, update)
        return execute_prediction(coords, update)
    else:
        update.message.reply_text("Sorry I didn't get that. Try again")

        return LOCATION


def stop(update: Update, _) -> int:
    update.message.reply_text("Alright, till next time! 👋")

    return ConversationHandler.END


def fallback(update: Update, _) -> int:
    update.message.reply_text("I didn't get that. Try again 👉 /find")

    return ConversationHandler.END


location_handler = ConversationHandler(
    entry_points=[CommandHandler("find", find)],
    states={
        LOCATION: [
            MessageHandler(
                (Filters.location | Filters.text)
                & (~Filters.regex(f"^(?i)stop$"))
                & (~Filters.command),
                location,
            )
        ],
    },
    fallbacks=[
        MessageHandler(Filters.regex(f"^(?i)stop$"), stop),
        MessageHandler(
            Filters.command,
            fallback,
        ),
    ],
)
