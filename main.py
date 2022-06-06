import os
import pandas as pd
import telegram

from google.cloud import bigquery
from operator import itemgetter as g
from predictor import Predictor

client = bigquery.Client()

def biodiversipy_bot(request):
    bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])

    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        chat_id = update.message.chat.id

        location = "TODO extract location from chat"

        predictor = Predictor(location, client)
        predictor.predict()

        bot.sendMessage(chat_id=chat_id, text=predictor.predictions_text)

    return "ok"
