import pandas as pd

TABLES = ['gee', 'worldclim', 'soilgrid']
COORD_COLUMNS = ['lon_lower', 'lon_upper' , 'lat_lower' , 'lat_upper']

def build_query(table, coords):
    lat, lon = coords
    print(f"Build query on {table} for lat={coords[0]}, lon={coords[1]}")

    return f"""
        SELECT *
        FROM `le-wagon-bootcamp-346910.features.{table}` as {table}
        WHERE ({table}.lat_lower <= {lat} AND {table}.lat_upper > {lat} AND {table}.lon_lower <= {lon} AND {table}.lon_upper > {lon})
        """

def get_coords(location):
    MOCK_LAT = 52.476920
    MOCK_LON = 13.408188
    return (MOCK_LAT, MOCK_LON)

def get_features(location, client):
    coords = get_coords(location)
    queries = [build_query(table, coords) for table in TABLES]

    features = pd.concat([
            client.query(query).to_dataframe().drop(columns=COORD_COLUMNS)
            for query in queries], axis=1)

    features['latitude'], features['longitude'] = coords

    try:
        assert features.shape == (1, 84)
    except:
        return f"Wrong shape {features.shape}"

    return features
