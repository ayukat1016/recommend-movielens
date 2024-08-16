from abc import ABC, abstractmethod
import itertools
import ast
import pandas as pd

from src.domain.preprocessed_data import ExtractedGenreSchema
from src.domain.preprocessed_data import ExtractedRatingSchema

from src.middleware.logger import configure_logger

logger = configure_logger(__name__)


class AbstractExtractor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def run(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        raise NotImplementedError


class RatingExtractor(AbstractExtractor):
    def __init__(self):
        pass

    def run(
        self,
        movielens_train: pd.DataFrame,  
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Extract statistics from price column.

        Args:
            df (pd.DataFrame): Input Pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame with year, month and day of week extracted.
        """
        aggregators: list = ["min", "max", "mean"]
        user_features = movielens_train.groupby("user_id").rating.agg(aggregators).to_dict()
        movie_features = movielens_train.groupby("movie_id").rating.agg(aggregators).to_dict()
        for agg in aggregators:
            df[f"u_{agg}"] = df["user_id"].map(user_features[agg])
            df[f"m_{agg}"] = df["movie_id"].map(movie_features[agg])

        # df = df.iloc[:, 4:]

        # ExtractedRatingSchema.validate(df)
        logger.info(
            f"""rating data extracted:
{df}
column:
{df.columns}
type:
{df.dtypes}
        """
        )
        return df


class GenreExtractor(AbstractExtractor):
    def __init__(self):
        pass

    def run(
        self,
        movies: pd.DataFrame,  
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """Extract statistics from price column.

        Args:
            df (pd.DataFrame): Input Pandas DataFrame.

        Returns:
            pd.DataFrame: DataFrame with year, month and day of week extracted.
        """
        movie_genres = movies[["movie_id", "genre"]].copy()
        movie_genres["genre"] = movie_genres["genre"].apply(ast.literal_eval)
        genres = list(set(itertools.chain(*movie_genres.genre)))
        genres = sorted(genres)

        for genre in genres:
            movie_genres.loc[:, f"is_{genre}"] = movie_genres.genre.apply(lambda x: genre in x)
        movie_genres.drop("genre", axis=1, inplace=True)
        df = df.merge(movie_genres, on="movie_id")

        # df = df.iloc[:, 10:]

        # ExtractedGenreSchema.validate(df)
        logger.info(
            f"""genre data extracted:
{df}
column:
{df.columns}
type:
{df.dtypes}
        """
        )
        return df

#         df_price = df[["id", "item_id", "store_id", "date_id", "sell_price"]].copy()
#         df_price["price_max"] = df_price.groupby(["store_id", "item_id"])[
#             "sell_price"
#         ].transform("max")
#         df_price["price_min"] = df_price.groupby(["store_id", "item_id"])[
#             "sell_price"
#         ].transform("min")
#         df_price["price_std"] = df_price.groupby(["store_id", "item_id"])[
#             "sell_price"
#         ].transform("std")
#         df_price["price_mean"] = df_price.groupby(["store_id", "item_id"])[
#             "sell_price"
#         ].transform("mean")
#         df_price["price_norm"] = df_price["sell_price"] / df_price["price_max"]
#         df_price["price_nunique"] = df_price.groupby(["store_id", "item_id"])[
#             "sell_price"
#         ].transform("nunique")
#         df_price["item_nunique"] = df_price.groupby(["store_id", "sell_price"])[
#             "item_id"
#         ].transform("nunique")

#         df = df_price.iloc[:, 5:]

#         ExtractedPriceSchema.validate(df)
#         logger.info(
#             f"""price data extracted:
# {df}
# column:
# {df.columns}
# type:
# {df.dtypes}
#         """
#         )
#         return df


# class LagSalesExtractor(AbstractExtractor):
#     def __init__(self):
#         pass

#     def run(
#         self,
#         df: pd.DataFrame,
#     ) -> pd.DataFrame:
#         """Extract lag from sales column.

#         Args:
#             df (pd.DataFrame): Input Pandas DataFrame.

#         Returns:
#             pd.DataFrame: DataFrame with year, month and day of week extracted.
#         """

#         df_lag = df[["id", "date_id", "sales"]]

#         num_lag_day_list = []
#         num_lag_day = 15
#         predict_horizon = 7
#         for col in range(predict_horizon, predict_horizon + num_lag_day):
#             num_lag_day_list.append(col)

#         num_rolling_day_list = [7, 14, 30, 60]
#         num_shift_rolling_day_list = []
#         for shift_day in [1, 7, 14]:
#             for num_rolling_day in [7, 14, 30]:
#                 num_shift_rolling_day_list.append([shift_day, num_rolling_day])

#         df_lag = df_lag.assign(
#             **{
#                 "lag_{}_{}".format(col, lag_day): df_lag.groupby(["id"])[
#                     "sales"
#                 ].transform(lambda x: x.shift(lag_day))
#                 for lag_day in num_lag_day_list
#             }
#         )

#         for col in range(len(df_lag.columns)):
#             if "lag" in str(col):
#                 df_lag[col] = df_lag[col]

#         for num_rolling_day in num_rolling_day_list:
#             df_lag["rolling_mean_" + str(num_rolling_day)] = df_lag.groupby(["id"])[
#                 "sales"
#             ].transform(
#                 lambda x: x.shift(predict_horizon).rolling(num_rolling_day).mean()
#             )
#             df_lag["rolling_std_" + str(num_rolling_day)] = df_lag.groupby(["id"])[
#                 "sales"
#             ].transform(
#                 lambda x: x.shift(predict_horizon).rolling(num_rolling_day).std()
#             )

#         df = df_lag.iloc[:, 3:]

#         ExtractedLagSalesSchema.validate(df)
#         logger.info(
#             f"""sales lag data extracted:
# {df}
# column:
# {df.columns}
# type:
# {df.dtypes}
#         """
#         )
#         return df
