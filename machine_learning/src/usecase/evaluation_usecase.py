from typing import List

import pandas as pd
from sklearn.metrics import mean_absolute_error  # type: ignore
from sklearn.metrics import mean_squared_error  # type: ignore

from src.domain.evaluation_data import Evaluation, FeatureImportances
from src.middleware.logger import configure_logger
from src.ml_algos.lightgbm_regressor import AbstractModel

logger = configure_logger(__name__)


class EvaluationUsecase(object):
    def __init__(self):
        pass

    def evaluate(
        self,
        user_id: List[str],
        timestamp_rank: List[str],
        movie_id: List[str],
        y_true: List[float],
        y_pred: List[float],
    ) -> Evaluation:
        logger.info(f"start evaluation...")
        rmse = (
            mean_squared_error(
                y_true=y_true,
                y_pred=y_pred,
            )
            ** 0.5
        )
        mae = mean_absolute_error(
            y_true=y_true,
            y_pred=y_pred,
        )
        d = [
            dict(
                user_id=u,
                timestamp_rank=r,
                movie_id=m,
                y_true=t,
                y_pred=p,
            )
            for u, r, m, t, p in zip(user_id, timestamp_rank, movie_id, y_true, y_pred)
        ]
        data = (
            pd.DataFrame(d)
            .sort_values(["user_id", "timestamp_rank"])
            .reset_index(drop=True)
        )
        logger.info(f"done evaluation")
        logger.info(
            f"""evaluation:
data:
{data}
mean_absolute_error: {mae}
root_mean_squared_error: {rmse}
        """
        )
        return Evaluation(
            data=data,
            root_mean_squared_error=rmse,
            mean_absolute_error=mae,
        )

    def export_feature_importance(
        self,
        model: AbstractModel,
    ) -> FeatureImportances:
        feature_importances = model.get_feature_importance()
        d = [f.model_dump() for f in feature_importances]
        data = (
            pd.DataFrame(d)
            .sort_values("importance", ascending=False)
            .reset_index(drop=True)
        )
        logger.info(
            f"""feature importances
{data}
        """
        )
        return FeatureImportances(feature_importances=data)
