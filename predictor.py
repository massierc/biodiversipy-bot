import logging
import os
import requests

from google.cloud import bigquery
from utils import get_features, get_species_img, get_species_description

from telegram.ext import ConversationHandler
from telegram import Update


logger = logging.getLogger(__name__)
MODEL_API_URL = os.environ["MODEL_API_URL"]


class Predictor:
    def __init__(self, coords):
        self.client = bigquery.Client()
        self.coords = coords
        self.features = get_features(coords, self.client)
        logger.info(f"features for coords {coords}", self.features)

    def predict(self):
        response = requests.get(MODEL_API_URL, params=self.features)
        json = response.json()
        logger.info(f"predictions for coords {self.coords}", json)
        self.predictions = json["species"]

        return self.predictions


def execute_prediction(coords: str, update: Update) -> int:
    message = update.message.reply_text("Got it! Just a minute ⌛")

    try:
        predictor = Predictor(coords)
        predictions = predictor.predict()

        # predictions = [
        #     {"species": "Chelidonium majus"},
        #     {"species": "Hedera helix"},
        #     {"species": "Echium vulgare"},
        #     {"species": "Bellis perennis"},
        #     {"species": "Glechoma hederacea"},
        # ]

        species = [prediction["species"] for prediction in predictions]

        most_likely = species[0]
        other_species = "\n".join(
            [f"{i + 2}. {sp}" for i, sp in enumerate(species[1:])]
        )

        message.edit_text(f"Good news, I found some plants! 🌱")
        update.message.reply_html(
            f"The plant you will most likely find here is <b>{species[0]}</b>:"
        )

        img = get_species_img(most_likely)
        if img:
            update.message.reply_photo(img)

        desc = get_species_description(most_likely)
        if desc:
            update.message.reply_html(f"<i>{desc}</i>")

        update.message.reply_text(
            f"\n\nThe next most likely plants here are:\n\n{other_species}"
        )

        return ConversationHandler.END
    except Exception as e:
        logger.error(e)
        message.edit_text(
            "An error occurred during the prediction, please try again 👉 /find",
        )
        return ConversationHandler.END
