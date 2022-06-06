import os
import pandas as pd
import telegram

from google.cloud import bigquery
from operator import itemgetter as g

def biodiversipy_bot(request):
    client = bigquery.Client()

    search_lat = 52.476920
    search_lon = 13.408188

    QUERY_GEE = f'''
    SELECT *
    FROM `le-wagon-bootcamp-346910.features.gee` as gee
    WHERE (gee.lat_lower <= {search_lat} AND gee.lat_upper > {search_lat} AND gee.lon_lower <= {search_lon} AND gee.lon_upper > {search_lon})
    '''

    QUERY_WORLDCLIM = f'''
    SELECT *
    FROM `le-wagon-bootcamp-346910.features.worldclim` as worldclim
    WHERE (worldclim.lat_lower <= {search_lat} AND worldclim.lat_upper > {search_lat} AND worldclim.lon_lower <= {search_lon} AND worldclim.lon_upper > {search_lon})
    '''

    QUERY_SOILGRID = f'''
    SELECT *
    FROM `le-wagon-bootcamp-346910.features.soilgrid` as soilgrid
    WHERE (soilgrid.lat_lower <= {search_lat} AND soilgrid.lat_upper > {search_lat} AND soilgrid.lon_lower <= {search_lon} AND soilgrid.lon_upper > {search_lon})
    '''

    coord_columns = ['lon_lower', 'lon_upper' , 'lat_lower' , 'lat_upper']

    gee_df = client.query(QUERY_GEE).to_dataframe().drop(columns=coord_columns)
    worldclim_df = client.query(QUERY_WORLDCLIM).to_dataframe().drop(columns=coord_columns)
    soilgrid_df = client.query(QUERY_SOILGRID).to_dataframe().drop(columns=coord_columns)

    df = pd.concat([gee_df, worldclim_df, soilgrid_df], axis=1)
    df['latitude'] = search_lat
    df['longitude'] = search_lon

    try:
        assert df.shape == (1, 84)
    except:
        return f"Wrong shape {df.shape}"

    return "ok"

    # bot = telegram.Bot(token=os.environ["TELEGRAM_TOKEN"])
    # if request.method == "POST":
    #     update = telegram.Update.de_json(request.get_json(force=True), bot)
    #     chat_id = update.message.chat.id
    #     # Reply with the same message
    #     bot.sendMessage(chat_id=chat_id, text=update.message.text)
    # return "okay"
