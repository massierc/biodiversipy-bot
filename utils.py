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
