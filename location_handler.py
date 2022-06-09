import logging

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    ConversationHandler,
)

from utils import get_coords, args_to_location, COORDS_ERROR
from predictor import execute_prediction

logger = logging.getLogger(__name__)


LOCATION = range(1)
LOCATION_KEYBOARD = ["Choose on map", "Send via text"]


def find(update: Update, context: CallbackContext) -> int:
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
        coords = get_coords(raw_location, update)

        if valid_coords(coords, update):
            return execute_prediction(coords, update)
        else:
            return LOCATION


def location(update: Update, _) -> int:
    user_location = update.message.location
    user_text = update.message.text

    if not user_location and not user_text:
        update.message.reply_text("Sorry I didn't get that. Try again")

        return LOCATION

    coords = get_coords(user_location or user_text)

    if valid_coords(coords, update):
        return execute_prediction(coords, update)
    else:
        return LOCATION


def valid_coords(coords, update):
    get_out_text = "Type `stop` at any time to get out."

    if coords == COORDS_ERROR["NOT_FOUND"]:
        update.message.reply_markdown(
            f"😖 Could not find {update.message.text}. Try with something else!\n\n{get_out_text}"
        )
        return False

    if coords == COORDS_ERROR["OOB"]:
        update.message.reply_markdown(
            f"I'm sorry, I can only look up places in Germany 🥨 try again!\n\n{get_out_text}"
        )
        return False

    return True


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
