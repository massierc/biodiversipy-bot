import logging
import os
import requests

from google.cloud import bigquery
from utils import get_features

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
        self.predictions_text = "\n".join(
            [
                f"{species['species']} - {species['probability']:.2%}"
                for species in self.predictions
            ]
        )


def execute_prediction(coords: str, update: Update) -> int:
    message = update.message.reply_text("Got it! Just a minute ⌛")

    if not coords:
        message.edit_text(
            f"😖 Could not find {update.message.text}. Try with something else!",
        )
        return ConversationHandler.END

    try:
        predictor = Predictor(coords)
        predictor.predict()

        text = "\n\n".join(
            [
                "Good news, I found some plants! 🌱",
                "Here are the results:",
                predictor.predictions_text,
            ]
        )

        message.edit_text(text)
        return ConversationHandler.END
    except Exception as e:
        logger.error(e)
        message.edit_text(
            "An error occurred during the prediction, please try again 👉 /find",
        )
        return ConversationHandler.END
