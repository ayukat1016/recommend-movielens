from typing import Tuple

import pandas as pd

from src.domain.common_data import XY
from src.domain.preprocessed_data import PreprocessedDataset
from src.domain.raw_data import RawDataset
from src.middleware.logger import configure_logger
from src.ml_algos.preprocess import AbstractExtractor

logger = configure_logger(__name__)


class PreprocessUsecase(object):
    def __init__(
        self,
        ratings_extractor: AbstractExtractor,
        genre_extractor: AbstractExtractor,
    ):
        """Preprocess usecase.

        Args:
            ratings_extractor (AbstractExtractor): Algorithm to extract ratings statitics.
            genre_extractor (AbstractExtractor): Algorithm to extract genre boolean.
        """
        self.ratings_extractor = ratings_extractor
        self.genre_extractor = genre_extractor

    def preprocess_dataset(
        self,
        dataset: RawDataset,
        validation_records: int,
    ) -> PreprocessedDataset:
        """Run preprocess for raw dataset.

        Args:
            dataset (RawDataset): Dataset to be transformed.

        Returns:
            PreprocessedDataset: Preprocessed data with separated to training and validation.
        """

        ratings_train, ratings_test = self.split_records(
            dataset.ratings_data, validation_records
        )

        train_keys_y = ratings_train[["user_id", "recency_id", "movie_id", "rating"]]
        test_keys_y = ratings_test[["user_id", "recency_id", "movie_id", "rating"]]

        df_train = train_keys_y.copy()
        df_test = test_keys_y.copy()

        df_train_rating = self.ratings_extractor.run(ratings_train, df_train)
        df_test_rating = self.ratings_extractor.run(ratings_train, df_test)

        df_train_genre = self.genre_extractor.run(dataset.movies_tags_data, df_train)
        df_test_genre = self.genre_extractor.run(dataset.movies_tags_data, df_test)

        df_train = pd.concat([df_train, df_train_rating, df_train_genre], axis=1)
        df_test = pd.concat([df_test, df_test_rating, df_test_genre], axis=1)

        average_rating = df_train["rating"].mean()
        df_test.fillna(average_rating, inplace=True)

        logger.info(f"transform training data...")
        training_data = self.split_columns(
            raw_data=df_train,
        )

        logger.info(f"transform validation data...")
        validation_data = self.split_columns(
            raw_data=df_test,
        )

        return PreprocessedDataset(
            training_data=training_data,
            validation_data=validation_data,
        )

    def split_records(
        self,
        ratings: pd.DataFrame,
        validation_records: int,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:

        ratings["recency_id"] = ratings.groupby("user_id")["timestamp"].rank(
            ascending=False, method="first"
        )
        ratings_train = ratings[ratings["recency_id"] > validation_records]
        ratings_test = ratings[ratings["recency_id"] <= validation_records]

        ratings_train = ratings_train.sort_values(
            ["user_id", "recency_id"]
        ).reset_index(drop=True)
        ratings_test = ratings_test.sort_values(["user_id", "recency_id"]).reset_index(
            drop=True
        )

        return (ratings_train, ratings_test)

    def split_columns(
        self,
        raw_data: pd.DataFrame,
    ) -> XY:
        """Transform DataFrame.

        Args:
            raw_data (pd.DataFrame): input data. Refer src/entity/raw_data/RawDataSchemafor the data format.

        Returns:
            XY: dataset to be used for model training, evaluation and prediction.
        """
        df = raw_data
        df = df.sort_values(["user_id", "recency_id"]).reset_index(drop=True)

        keys = df[["user_id", "recency_id", "movie_id"]]
        data = self.split_data_target(
            keys=keys,
            data=df,
        )

        logger.info(
            f"""done preprocessing dataset:
x columns:
{data.x.columns}
x:
{data.x}
y:
{data.y}
        """
        )
        return data

    def split_data_target(
        self,
        keys: pd.DataFrame,
        data: pd.DataFrame,
    ) -> XY:
        """Split data into training data x and target data y.

        Args:
            keys (pd.DataFrame): keys in order.
            data (pd.DataFrame): data in order.

        Returns:
            XY: training data x and target data y.
        """
        y = data[["rating"]]
        x = data.drop(
            ["user_id", "recency_id", "movie_id", "rating"],
            axis=1,
        )
        return XY(
            keys=keys,
            x=x,
            y=y,
        )
