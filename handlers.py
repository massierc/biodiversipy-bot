from telegram import Update
from telegram.ext import (
    CommandHandler,
    Dispatcher,
    CallbackContext,
)


def start(update: Update, context: CallbackContext):
    text = "\n\n".join(
        [f"Welcome to {context.bot.first_name}!", "Get started here 👉 /help"]
    )
    update.message.reply_text(text)


def help(update: Update, _: CallbackContext):
    text = "\n\n".join(
        [
            "The following commands are available:",
            "📍 /find `location` • Returns the probability of finding a species at the specified location",
            "🙋‍♀️ /help • Come back here",
        ]
    )
    update.message.reply_markdown(text)


def find(update: Update, context: CallbackContext):
    location = " ".join([arg.capitalize() for arg in context.args])
    update.message.reply_text(
        f"Finding plants in {location}, this will take a few moments..."
    )


command_handlers = [
    ("start", start),
    ("help", help),
    ("find", find),
]


def register_handlers(dispatcher: Dispatcher):
    for (id, fn) in command_handlers:
        dispatcher.add_handler(CommandHandler(id, fn))
