import pandas as pd

from src.domain.prediction_data import Prediction, PredictionDataset, Recommendation
from src.middleware.logger import configure_logger
from src.ml_algos.lightgbm_regressor import AbstractModel

logger = configure_logger(__name__)


class PredictionUsecase(object):
    def __init__(self):
        pass

    def predict(
        self,
        model: AbstractModel,
        data: PredictionDataset,
    ) -> Prediction:
        logger.info(f"start prediction: {model.name}...")

        prediction = model.predict(x=data.prediction_data.x.reset_index(drop=True))

        d = [
            dict(
                user_id=u,
                timestamp_rank=r,
                movie_id=m,
                prediction=p,
            )
            for u, r, m, p in zip(
                data.prediction_data.keys["user_id"].tolist(),
                data.prediction_data.keys["timestamp_rank"].tolist(),
                data.prediction_data.keys["movie_id"].tolist(),
                prediction,
            )
        ]
        df = (
            pd.DataFrame(d)
            .sort_values(["user_id", "timestamp_rank"])
            .reset_index(drop=True)
        )
        prediction_output = Prediction(data=df)

        logger.info(f"done prediction: {model.name}")
        logger.info(
            f"""prediction:
{prediction_output.data}
        """
        )
        return prediction_output

    def recommend(
        self,
        model: AbstractModel,
        data: PredictionDataset,
    ) -> Recommendation:
        logger.info(f"start recommendation: {model.name}...")

        prediction = model.predict(x=data.prediction_data.x.reset_index(drop=True))

        d = [
            dict(
                user_id=u,
                movie_id=m,
                prediction=p,
            )
            for u, m, p in zip(
                data.prediction_data.keys["user_id"].tolist(),
                data.prediction_data.keys["movie_id"].tolist(),
                prediction,
            )
        ]
        df = (
            pd.DataFrame(d)
            .sort_values(["user_id", "prediction"], ascending=[True, False])
            .reset_index(drop=True)
        )
        recommendation_output = Recommendation(data=df)

        logger.info(f"done recommendation: {model.name}")
        logger.info(
            f"""recommendation:
{recommendation_output.data}
        """
        )
        return recommendation_output
