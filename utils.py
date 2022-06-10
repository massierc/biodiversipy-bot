import logging
import pandas as pd
import re
import requests

from bs4 import BeautifulSoup
from logging import Logger
from geopy.geocoders import Nominatim
from google.cloud import bigquery
from typing import Tuple

from telegram import Update

logger = logging.getLogger(__name__)

TABLES = ["worldclim", "gee", "soilgrid"]
COORD_COLUMNS = ["lon_lower", "lon_upper", "lat_lower", "lat_upper"]


def build_query(table, coords):
    lat, lon = coords
    print(f"Build query on {table} for lat={coords[0]}, lon={coords[1]}")

    return f"""
        SELECT *
        FROM `le-wagon-bootcamp-346910.features.{table}` as {table}
        WHERE ({table}.lat_lower <= {lat} AND {table}.lat_upper > {lat} AND {table}.lon_lower <= {lon} AND {table}.lon_upper > {lon})
        """


COORDS_ERROR = {
    "NOT_FOUND": "NOT_FOUND",
    "OOB": "OOB",
}


def get_coords(raw_location):
    if not isinstance(raw_location, str):
        return (raw_location.latitude, raw_location.longitude)

    logger.info(f"Looking for coordinates for {raw_location}")

    geolocator = Nominatim(user_agent="biodiversipy_bot")
    location = geolocator.geocode(raw_location, language="en")

    if not location:
        return COORDS_ERROR["NOT_FOUND"]

    coords = (location.latitude, location.longitude)
    address = location.address
    country = address.replace(" ", "").split(",")[-1]

    if not country == "Germany":
        return COORDS_ERROR["OOB"]

    logger.info(f"ADDRESS: {address} - LAT, LON: {coords}")

    return coords


def get_features(coords: Tuple[float, float], client: bigquery.Client):
    queries = [build_query(table, coords) for table in TABLES]

    features = pd.concat(
        [
            client.query(query).to_dataframe().drop(columns=COORD_COLUMNS)
            for query in queries
        ],
        axis=1,
    )

    features.insert(0, "latitude", coords[0])
    features.insert(1, "longitude", coords[1])

    try:
        assert features.shape == (1, 84)
    except:
        return f"Wrong shape {features.shape}"

    return features.to_dict("records")[0]


def args_to_location(args):
    return " ".join([arg.capitalize() for arg in args])


def get_species_description(scientific_name):
    query = scientific_name.replace(" ", "_")
    html = requests.get(f"https://en.wikipedia.org/wiki/{query}")
    soup = BeautifulSoup(html.text, "html.parser")
    raw_text = "".join(soup.select("p")[1].find_all(text=True))
    text = re.sub("\[\d+\]", "", raw_text)

    return text


def get_species_img(scientific_name):
    query = scientific_name.replace(" ", "_")
    html = requests.get(f"https://en.wikipedia.org/wiki/{query}")
    soup = BeautifulSoup(html.text, "html.parser")
    url_bit = soup.select("img")[0].get("srcset").split(",")[1][:-2].strip()
    full_url = "https:" + url_bit

    return full_url


def log_update(update: Update, logger: Logger = logger):
    try:
        message = update.message
        first_name = message.chat.first_name or ""
        last_name = message.chat.last_name or ""
        username = message.chat.username
        full_name = first_name + last_name
        form_username = f"@{username}" if username else ""
        form_full_name = f"[{full_name}]" if full_name else ""
        entry = f"::update:: {form_username}{form_full_name} - {message.text}"
        logger.info(entry)
    except Exception as e:
        logger.error(f"An error occurred on log_update: {e}")


def valid_coords(coords, update):
    get_out_text = "Type `stop` at any time to get out."

    if coords == COORDS_ERROR["NOT_FOUND"]:
        update.message.reply_markdown(
            f"😖 Could not find {update.message.text}. Try with something else!\n\n{get_out_text}"
        )
        return False

    if coords == COORDS_ERROR["OOB"]:
        update.message.reply_markdown(
            f"I'm sorry, I can only look up places in Germany 🥨 try again!\n\n{get_out_text}"
        )
        return False

    return True
