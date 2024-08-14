import itertools
import ast


import pandas as pd
from typing import Tuple
from src.domain.common_data import XY
from src.domain.preprocessed_data import PreprocessedDataset
from src.domain.raw_data import RawDataset
from src.middleware.logger import configure_logger
# from src.ml_algos.preprocess import AbstractExtractor

logger = configure_logger(__name__)


class PreprocessUsecase(object):
    def __init__(
        self,
        # rating_extractor: AbstractExtractor,
        # lag_sales_extractor: AbstractExtractor,
    ):
        """Preprocess usecase.

        Args:
            prices_extractor (AbstractExtractor): Algorithm to extract prices statitics.
            lag_sales_extractor (AbstractExtractor): Algorithm to extract lag sales data.
        """
        # self.prices_extractor = prices_extractor
        # self.lag_sales_extractor = lag_sales_extractor

    def preprocess_dataset(
        self,
        dataset: RawDataset,
    ) -> PreprocessedDataset:
        """Run preprocess for raw dataset.

        Args:
            dataset (RawDataset): Dataset to be transformed.

        Returns:
            PreprocessedDataset: Preprocessed data with separated to training, validation and prediction.
        """

        movielens_train, movielens_test = self.split_records(dataset.data_movielens)
        
        train_keys_y = movielens_train[["user_id", "movie_id", "rating"]]
        test_keys_y = movielens_test[["user_id", "movie_id", "rating"]]

        df_train = train_keys_y.copy()
        df_test = test_keys_y.copy()

        aggregators: list = ["min", "max", "mean"]
        user_features = movielens_train.groupby("user_id").rating.agg(aggregators).to_dict()
        movie_features = movielens_train.groupby("movie_id").rating.agg(aggregators).to_dict()
        for agg in aggregators:
            df_train[f"u_{agg}"] = df_train["user_id"].map(user_features[agg])
            df_test[f"u_{agg}"] = df_test["user_id"].map(user_features[agg])
            df_train[f"m_{agg}"] = df_train["movie_id"].map(movie_features[agg])
            df_test[f"m_{agg}"] = df_test["movie_id"].map(movie_features[agg])

        average_rating = df_train["rating"].mean()
        df_test.fillna(average_rating, inplace=True)


        movie_genres = dataset.data_movies[["movie_id", "genre"]].copy()
        movie_genres["genre"] = movie_genres["genre"].apply(ast.literal_eval)
        genres = list(set(itertools.chain(*movie_genres.genre)))
        genres = sorted(genres)

        for genre in genres:
            movie_genres.loc[:, f"is_{genre}"] = movie_genres.genre.apply(lambda x: genre in x)
        movie_genres.drop("genre", axis=1, inplace=True)
        df_train = df_train.merge(movie_genres, on="movie_id")
        df_test = df_test.merge(movie_genres, on="movie_id")

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
        movielens: pd.DataFrame,
    ) ->  Tuple[pd.DataFrame, pd.DataFrame]:
        
        movielens['timestamp_rank'] = movielens.groupby(
            'user_id')['timestamp'].rank(ascending=False, method='first')
        movielens_train = movielens[movielens['timestamp_rank'] > 5]
        movielens_test = movielens[movielens['timestamp_rank']<= 5]

        return (movielens_train, movielens_test)


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
        df = df.sort_values(["user_id", "movie_id"]).reset_index(drop=True)

        keys = df[["user_id", "movie_id"]]
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
            ["user_id", "movie_id", "rating"],
            axis=1,
        )
        return XY(
            keys=keys,
            x=x,
            y=y,
        )
