import logging

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    ConversationHandler,
)

from utils import get_coords, args_to_location, log_update, valid_coords
from predictor import execute_prediction

logger = logging.getLogger(__name__)


LOCATION = range(1)
LOCATION_KEYBOARD = ["Choose on map", "Send via text"]


def find(update: Update, context: CallbackContext) -> int:
    log_update(update, logger)
    if len(context.args) == 0:
        text = "\n\n".join(
            [
                "Alright let's go! You have two options:",
                "`📍  `You can share your location from the menu button (📎) below",
                "`✍️  `Or you can just type an address",
            ]
        )
        update.message.reply_markdown(text)

        return LOCATION
    else:
        raw_location = args_to_location(context.args)
        coords = get_coords(raw_location)

        if valid_coords(coords, update):
            execute_prediction(coords, update)
            return ConversationHandler.END
        else:
            return LOCATION


def location(update: Update, _) -> int:
    log_update(update, logger)
    user_location = update.message.location
    user_text = update.message.text

    if not user_location and not user_text:
        update.message.reply_text("Sorry I didn't get that. Try again")

        return LOCATION

    coords = get_coords(user_location or user_text)

    if valid_coords(coords, update):
        execute_prediction(coords, update)
        return ConversationHandler.END
    else:
        return LOCATION


def stop(update: Update, _) -> int:
    log_update(update, logger)
    update.message.reply_text("Alright, till next time! 👋")

    return ConversationHandler.END


def fallback(update: Update, _) -> int:
    log_update(update, logger)
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
