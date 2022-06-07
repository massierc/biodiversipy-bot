import os
import logging

from handlers import register_handlers
from queue import Queue

from telegram.ext import Updater, Dispatcher
from telegram import Bot, Update

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def biodiversipy_bot(request):
    bot = Bot(os.environ["TELEGRAM_TOKEN"])
    update_queue = Queue()
    dispatcher = Dispatcher(bot, update_queue)
    register_handlers(dispatcher)

    if request.method == "POST":
        json = request.get_json(force=True)
        update = Update.de_json(json, bot)
        dispatcher.process_update(update)

    return "ok"


def main():
    bot = Bot(os.environ["TELEGRAM_TOKEN"])
    updater = Updater(bot=bot, use_context=True)
    register_handlers(updater.dispatcher)
    updater.start_polling()


if __name__ == "__main__":
    main()
