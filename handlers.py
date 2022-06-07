from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Dispatcher,
    Filters,
    MessageHandler,
)


def start(update: Update, context: CallbackContext):
    text = "\n\n".join(
        [f"Welcome to {context.bot.first_name}!", "Get started here 👉 /help"]
    )
    update.message.reply_text(text)


def help(update: Update, _):
    text = "\n\n".join(
        [
            "The following commands are available:",
            "📍 /find `location` • Returns the probability of finding a species at the specified location",
            "🙋‍♀️ /help • Come back here",
        ]
    )
    update.message.reply_markdown(text)


def find(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_markdown("Please provide a location: /find `location`")
    else:
        location = " ".join([arg.capitalize() for arg in context.args])
        update.message.reply_text(
            f"Finding plants in {location}, this will take a few moments..."
        )


def unknown(update: Update, _):
    text = "\n\n".join(["Sorry I didn't get it. I'm a simple bot 🙈", "Try /help"])
    update.message.reply_text(text)


command_handlers = [
    ("start", start),
    ("help", help),
    ("find", find),
    ("find", find),
]

message_handlers = [("unknown", unknown, Filters.text & (~Filters.command))]


def register_handlers(dispatcher: Dispatcher):
    for (id, fn) in command_handlers:
        dispatcher.add_handler(CommandHandler(id, fn))

    for (id, fn, filters) in message_handlers:
        dispatcher.add_handler(MessageHandler(filters, unknown))
