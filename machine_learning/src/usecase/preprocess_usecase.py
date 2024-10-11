from typing import Tuple

import pandas as pd

from src.domain.algorithm.preprocess import AbstractExtractor
from src.domain.model.common_data import XY
from src.domain.model.preprocessed_data import PreprocessedDataset
from src.domain.model.raw_data import RawDataset
from src.middleware.logger import configure_logger

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

        logger.info(f"done split records")
        logger.info(
            f"""train ratings:
{ratings_train}
column:
{ratings_train.columns}
type:
{ratings_train.dtypes}
        """
        )

        logger.info(
            f"""test ratings:
{ratings_test}
column:
{ratings_test.columns}
type:
{ratings_test.dtypes}
        """
        )

        train_keys_y = ratings_train[
            ["user_id", "timestamp_rank", "movie_id", "rating"]
        ]
        test_keys_y = ratings_test[["user_id", "timestamp_rank", "movie_id", "rating"]]

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

        ratings["timestamp_rank"] = (
            ratings.groupby("user_id")["timestamp"]
            .rank(ascending=False, method="first")
            .astype(int)
        )
        ratings_train = ratings[ratings["timestamp_rank"] > validation_records]
        ratings_test = ratings[ratings["timestamp_rank"] <= validation_records]

        ratings_train = ratings_train.sort_values(
            ["user_id", "timestamp_rank"]
        ).reset_index(drop=True)
        ratings_test = ratings_test.sort_values(
            ["user_id", "timestamp_rank"]
        ).reset_index(drop=True)

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
        df = df.sort_values(["user_id", "timestamp_rank"]).reset_index(drop=True)

        keys_df = df[["user_id", "timestamp_rank", "movie_id"]]
        data_df = df.drop(["user_id", "timestamp_rank", "movie_id"], axis=1)
        data = self.split_data_target(
            keys=keys_df,
            data=data_df,
        )

        logger.info(
            f"""done preprocessing dataset:
keys columns:
{data.keys.columns}
keys:
{data.keys}
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
        x = data.drop(["rating"], axis=1)
        return XY(
            keys=keys,
            x=x,
            y=y,
        )
