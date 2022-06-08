import logging

from google.cloud import bigquery
from utils import get_features

from telegram.ext import ConversationHandler
from telegram import Update, ReplyKeyboardRemove


logger = logging.getLogger(__name__)


class Predictor:
    def __init__(self, coords):
        self.client = bigquery.Client()
        self.features = get_features(coords, self.client)

    def predict(self):
        self.predictions = [
            ("Some species", 0.23),
            ("Some other species", 0.15),
            ("A third species", 0.04),
        ]
        self.predictions_text = "\n".join(
            [f"{species[0]} - {species[1]:.2%}" for species in self.predictions]
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

        message.edit_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    except Exception as e:
        logger.error(e)
        message.edit_text(
            "An error occurred during the prediction, please try again.",
        )
        return ConversationHandler.END
