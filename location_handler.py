import logging
import time


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
INSTRUCTIONS_MARKDOWN = "\n".join(
    [
        "`📍  `You can share your location from the menu button (📎) below",
        "`✍️  `Or you can just type an address",
    ]
)


def find(update: Update, context: CallbackContext) -> int:
    log_update(update, logger)
    if len(context.args) == 0:
        text = "\n\n".join(
            ["Alright let's go! You have two options:", INSTRUCTIONS_MARKDOWN]
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

    if user_text and user_text.lower() in ["lewagon berlin", "le wagon berlin"]:
        return lewagon(update)

    if not user_location and not user_text:
        update.message.reply_text("Sorry I didn't get that. Try again")

        return LOCATION

    coords = get_coords(user_location or user_text)

    if valid_coords(coords, update):
        execute_prediction(coords, update)
        return ConversationHandler.END
    else:
        return LOCATION


def lewagon(update: Update):
    message = update.message.reply_text("Got it! Just a minute ⌛")
    time.sleep(3)
    message.edit_text(f"Good news, I found some plants! 🌱")

    update.message.reply_html(
        f"The plant you will most likely find here is <b>Mikkelius Wagonius</b>:"
    )
    update.message.reply_photo(open("assets/mikkelus-wagonius.JPG", "rb"))
    update.message.reply_html(
        "<i>The Mikkelus Wagonius VK, most commonly known as the 'Viking climbing 7s', is an aggressive seasonal plant native to Danish villages. Via 9-euro-ticket and 30 cent gas discount it has been introduced to Berlin, and is largely considered an invasive species, particularly on volleyball courts. Uprooting or cutting the plant is an effective means of control.</i>"
    )
    return ConversationHandler.END


def stop(update: Update, _) -> int:
    log_update(update, logger)
    update.message.reply_text("Alright, till next time! 👋")

    return ConversationHandler.END


def fallback(update: Update, _) -> int:
    log_update(update, logger)
    update.message.reply_markdown(f"I didn't get that 🙈\n\n{INSTRUCTIONS_MARKDOWN}")

    return LOCATION


LEWAGON_FILTER = Filters.regex(f"^(?i)lewagon berlin$")

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
