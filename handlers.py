import html
import json
import logging
import traceback
import os

from telegram import Update, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Dispatcher,
    Filters,
    MessageHandler,
    ConversationHandler,
)


from predictor import Predictor
from utils import get_coords, args_to_location

logger = logging.getLogger(__name__)

DEVELOPER_CHAT_ID = os.environ["DEVELOPER_CHAT_ID"]


def start(update: Update, context: CallbackContext):
    text = "\n\n".join(
        [f"Welcome to {context.bot.first_name}!", "Get started here 👉 /help"]
    )
    update.message.reply_text(text)


def about(update: Update, context: CallbackContext):
    text = "\n".join(
        [
            f"🔍 {context.bot.first_name} is an AI tool developed for educational and demonstration purposes only.\n",
            "🗺️ <code>Input  </code> A location in Germany",
            "🌿 <code>Output </code> The 5 plant species most likely present at that location\n",
            "The model was trained using about 2 million observations in Germany. It makes predictions using environmental features retrieved from open-access databases:\n",
            "⛅️ Bioclimatic data, like temperature and precipitations",
            "🪨 Soil properties, like pH and CEC",
            "⛰️ Topographic data, like elevation\n",
            "<i>Source code, data sources, licenses and disclaimers on https://github.com/TmtStss/biodiversipy</i>",
        ]
    )
    update.message.reply_html(text, disable_web_page_preview=True)


def execute_prediction(coords: str, update: Update) -> int:
    message = update.message.reply_text("Got it! Just a minute ⌛")

    try:
        predictor = Predictor(coords)
        predictor.predict()

        text = "\n\n".join(
            [
                "Good news, I found some plants! 🌱",
                "Here are the results:",
                predictor.predictions_text,
            ]
        )

        message.edit_text(text)
        return ConversationHandler.END
    except:
        message.edit_text("An error occurred during the prediction, please try again.")
        return ConversationHandler.END


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


def bad_command(_: Update, context: CallbackContext):
    """Raise an error to trigger the error handler."""
    context.bot.wrong_method_name()


def unknown(update: Update, _):
    text = "\n\n".join(
        ["Sorry, I didn't get it. I'm a simple bot 🙈", "Check my commands below 👇"]
    )
    update.message.reply_text(text)


def error_handler(update: Update, context: CallbackContext):
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__
    )
    tb_string = "".join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f"An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    update.message.reply_text("Sorry, an error occurred. Try again!")

    if DEVELOPER_CHAT_ID:
        context.bot.send_message(
            chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML
        )

    return ConversationHandler.END


command_handlers = [
    ("start", start),
    ("about", about),
    ("kaboom", bad_command),
]

message_handlers = [("unknown", unknown, Filters.text & (~Filters.command))]


def register_handlers(dispatcher: Dispatcher):
    for (id, fn) in command_handlers:
        dispatcher.add_handler(CommandHandler(id, fn))

    dispatcher.add_handler(location_handler)
    for (id, fn, filters) in message_handlers:
        dispatcher.add_handler(MessageHandler(filters, unknown))

    dispatcher.add_error_handler(error_handler)
