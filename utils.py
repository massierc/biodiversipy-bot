import logging
import pandas as pd

from geopy.geocoders import Nominatim
from google.cloud import bigquery
from typing import Tuple

logger = logging.getLogger(__name__)

TABLES = ["gee", "worldclim", "soilgrid"]
COORD_COLUMNS = ["lon_lower", "lon_upper", "lat_lower", "lat_upper"]


def build_query(table, coords):
    lat, lon = coords
    print(f"Build query on {table} for lat={coords[0]}, lon={coords[1]}")

    return f"""
        SELECT *
        FROM `le-wagon-bootcamp-346910.features.{table}` as {table}
        WHERE ({table}.lat_lower <= {lat} AND {table}.lat_upper > {lat} AND {table}.lon_lower <= {lon} AND {table}.lon_upper > {lon})
        """


def get_coords(raw_location, update=None):
    logger.info(f"Looking for coordinates for {raw_location}")

    geolocator = Nominatim(user_agent="biodiversipy_bot")
    location = geolocator.geocode(raw_location)

    if not location:
        return None

    coords = (location.latitude, location.longitude)
    address = location.address

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

    features["latitude"], features["longitude"] = coords

    try:
        assert features.shape == (1, 84)
    except:
        return f"Wrong shape {features.shape}"

    return features


def args_to_location(args):
    return " ".join([arg.capitalize() for arg in args])
