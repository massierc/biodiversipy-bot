from google.cloud import bigquery
from utils import get_features


class Predictor:
    def __init__(self, location):
        self.client = bigquery.Client()
        self.features = get_features(location, self.client)

    def predict(self):
        self.predictions = [
            ("Some species", 0.23),
            ("Some other species", 0.15),
            ("A third species", 0.04),
        ]
        self.predictions_text = "\n".join(
            [f"{species[0]} - {species[1]:.2%}" for species in self.predictions]
        )
