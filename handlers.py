import html
import json
import logging
import traceback
import os

from telegram import Update, ParseMode
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Dispatcher,
    Filters,
    MessageHandler,
)


from predictor import Predictor
from utils import get_coords

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
            "🗺️ <b>Input</b>: a location in Germany",
            "🌿 <b>Output</b>: the 5 plant species most likely present.\n",
            "The model was trained using about 2 million observations in Germany. It makes predictions using environmental features retrieved from open-access databases:\n",
            "⛅️ Bioclimatic data, like temperature and precipitations",
            "🪨 Soil properties, like pH and CEC",
            "⛰️ Topographic data, like elevation\n",
            "<i>Source code, data sources, licenses and disclaimers on https://github.com/TmtStss/biodiversipy</i>",
        ]
    )
    update.message.reply_html(text, disable_web_page_preview=True)


def find(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_markdown("Please provide a location: /find `location`")
    else:
        message = update.message.reply_text("Got it! Just a minute.")

        location = " ".join([arg.capitalize() for arg in context.args])
        coords, address = get_coords(location)

        message.edit_text(f"Finding plants in {address}")
        message = update.message.reply_text("This will take a moment ⌛")

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


def bad_command(_: Update, context: CallbackContext):
    """Raise an error to trigger the error handler."""
    context.bot.wrong_method_name()


def unknown(update: Update, _):
    text = "\n\n".join(["Sorry, I didn't get it. I'm a simple bot 🙈", "Try /help"])
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


command_handlers = [
    ("start", start),
    ("about", about),
    ("find", find),
    ("kaboom", bad_command),
]

message_handlers = [("unknown", unknown, Filters.text & (~Filters.command))]


def register_handlers(dispatcher: Dispatcher):
    for (id, fn) in command_handlers:
        dispatcher.add_handler(CommandHandler(id, fn))

    for (id, fn, filters) in message_handlers:
        dispatcher.add_handler(MessageHandler(filters, unknown))

    dispatcher.add_error_handler(error_handler)
