import logging

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
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


LOCATION_PROMPT, LOCATION_FROM_MAP, LOCATION_FROM_TEXT = range(3)
LOCATION_KEYBOARD = ["Choose on map", "Send via text"]


def find(update: Update, context: CallbackContext) -> int:
    if len(context.args) == 0:
        update.message.reply_markdown(
            "Where should I look?",
            reply_markup=ReplyKeyboardMarkup(
                [LOCATION_KEYBOARD],
                one_time_keyboard=True,
            ),
        )

        return LOCATION_PROMPT
    else:
        raw_location = args_to_location(context.args)
        coords = get_coords(raw_location, update)
        return execute_prediction(coords, update)


def location_prompt(update: Update, _) -> int:
    if update.message.text == LOCATION_KEYBOARD[0]:
        update.message.reply_text("Plese send me a location 📍")

        return LOCATION_FROM_MAP
    elif update.message.text == LOCATION_KEYBOARD[1]:
        update.message.reply_text("Which location?")

        return LOCATION_FROM_TEXT
    else:
        update.message.reply_text("Sorry I didn't get that.")

    return ConversationHandler.END


def map_location(update: Update, _):
    user_location = update.message.location

    if user_location:
        coords = (user_location.latitude, user_location.longitude)
        return execute_prediction(coords, update)
    else:
        update.message.reply_text(
            "I didn't get that. Please send me a valid location 📍"
        )
        return LOCATION_FROM_MAP


def text_location(update: Update, _):
    location = update.message.text
    coords = get_coords(location, update)
    return execute_prediction(coords, update)


def cancel(update: Update) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text("See you!", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


location_handler = ConversationHandler(
    entry_points=[CommandHandler("find", find)],
    states={
        LOCATION_PROMPT: [
            MessageHandler(
                Filters.regex(f"^({LOCATION_KEYBOARD[0]}|{LOCATION_KEYBOARD[1]})$"),
                location_prompt,
            )
        ],
        LOCATION_FROM_MAP: [
            MessageHandler(
                Filters.location,
                map_location,
            )
        ],
        LOCATION_FROM_TEXT: [
            MessageHandler(
                Filters.text & (~Filters.command),
                text_location,
            )
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
