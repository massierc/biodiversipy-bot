import os
import pandas as pd
import telegram

from google.cloud import bigquery
from operator import itemgetter as g
from utils import build_query, get_coords

TABLES = ['gee', 'worldclim', 'soilgrid']
COORD_COLUMNS = ['lon_lower', 'lon_upper' , 'lat_lower' , 'lat_upper']

client = bigquery.Client()

def biodiversipy_bot(request):
    bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])

    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        chat_id = update.message.chat.id

        location = "TODO extract location from chat"
        coords = get_coords(location)

        queries = [
            build_query(table, coords)
            for table in TABLES]

        df = pd.concat([
            client\
                .query(query)\
                .to_dataframe()\
                .drop(columns=COORD_COLUMNS)
            for query in queries], axis=1)

        df['latitude'], df['longitude'] = coords

        try:
            assert df.shape == (1, 84)
        except:
            return f"Wrong shape {df.shape}"

        bot.sendMessage(chat_id=chat_id, text=df.to_string())

    return "ok"
