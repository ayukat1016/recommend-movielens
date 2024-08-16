import pandas as pd

from src.domain.training_data import TrainingDataset
from src.middleware.logger import configure_logger
from src.ml_algos.lightgbm_regressor import AbstractModel

logger = configure_logger(__name__)


class TrainingUsecase(object):
    def __init__(self):
        pass

    def train(
        self,
        model: AbstractModel,
        training_data: TrainingDataset,
    ):
        logger.info(f"start training: {model.name}...")

        model.train(
            x_train=training_data.training_data.x.reset_index(drop=True),
            y_train=training_data.training_data.y.squeeze().reset_index(drop=True),
            x_test=training_data.validation_data.x.reset_index(drop=True),
            y_test=training_data.validation_data.y.squeeze().reset_index(drop=True),
        )
        logger.info(f"done training: {model.name}")
