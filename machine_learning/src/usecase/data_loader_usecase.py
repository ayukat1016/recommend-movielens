from typing import List, Tuple
import numpy as np
import pandas as pd

from src.domain.raw_data import RawDataset
from src.middleware.logger import configure_logger
from src.repository.movies_repository import AbstractMoviesRepository
from src.repository.ratings_repository import AbstractRatingsRepository
from src.repository.tags_repository import AbstractTagsRepository
from src.schema.movies_schema import Movies
from src.schema.ratings_schema import Ratings
from src.schema.tags_schema import Tags

logger = configure_logger(__name__)


class DataLoaderUsecase(object):
    def __init__(
        self,
        movies_repository: AbstractMoviesRepository,
        ratings_repository: AbstractRatingsRepository,
        tags_repository: AbstractTagsRepository,
    ):
        """Data loader usecase.

        Args:
            calendar_repository (AbstractCalendarRepository): Repository to load data for calendar.
            prices_repository (AbstractPricesRepository): Repository to load data for prices.
            sales_calendar_repository  (AbstractSalesCalendarRepository): Repository to load data for training.
        """

        self.movies_repository = movies_repository
        self.ratings_repository = ratings_repository
        self.tags_repository = tags_repository

    def load_dataset(self) -> RawDataset:
        """Load dataset for training, validation and prediction.

        Returns:
            RawDataset: Data loaded from database.
        """
        # movielens_df, movies_df= self.load_data()
        # movielens_train, movielens_test = self.split_data(movielens)
        # data_train = RawDataRatings(data=movielens_train)
        # data_test = RawDataRatings(data=movielens_test)

        logger.info(f"load data from database")

        movies_data = self.load_movies_data()
        movies_dataset_dict = [d.dict() for d in movies_data]
        movies_df = pd.DataFrame(movies_dataset_dict)

        ratings_data = self.load_ratings_data()
        ratings_dataset_dict = [d.dict() for d in ratings_data]
        ratings_df = pd.DataFrame(ratings_dataset_dict)

        tags_data = self.load_tags_data()
        tags_dataset_dict = [d.dict() for d in tags_data]
        tags_df = pd.DataFrame(tags_dataset_dict)

        movies_tags_df = tags_df.groupby('movie_id').agg({'tag':list})
        movies_df = movies_df.merge(movies_tags_df, on="movie_id", how="left")
        movielens_df = ratings_df.merge(movies_df, on='movie_id', how="left")

        return RawDataset(
            data_movielens=movielens_df,
            data_movies=movies_df,
        )
            

#     def load_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
#         """Load data.

#         Returns:
#             pd.DataFrame: Training and validation data.
#         """

#         # logger.info(f"load data from: {date_from} to {date_to}")
#         # data = self.load_sales_calendar_data(
#         #     date_from=date_from,
#         #     date_to=date_to,
#         # )

#         logger.info(f"load data from database")

#         movies_data = self.load_movies_data()
#         movies_dataset_dict = [d.dict() for d in movies_data]
#         movies_df = pd.DataFrame(movies_dataset_dict)

#         ratings_data = self.load_ratings_data()
#         ratings_dataset_dict = [d.dict() for d in ratings_data]
#         ratings_df = pd.DataFrame(ratings_dataset_dict)

#         tags_data = self.load_tags_data()
#         tags_dataset_dict = [d.dict() for d in tags_data]
#         tags_df = pd.DataFrame(tags_dataset_dict)

#         movies_tags_df = tags_df.groupby('movie_id').agg({'tag':list})
#         movies_df = movies_df.merge(movies_tags_df, on="movie_id", how="left")
#         movielens_df = ratings_df.merge(movies_df, on='movie_id', how="left")

#         # print(movies_df)
#         # print(ratings_df)
#         # print(tags_df)
#         # print(movies_tags_df)        
#         # print(movielens_df)

# #         df = movielens_df

# #         logger.info(f"loaded: {df.shape}")
# #         logger.info(
# #             f"""df:
# # {df}
# # column:
# # {df.columns}
# # type:
# # {df.dtypes}
# #         """
# #         )
#         return (movielens_df, movies_df)


    def load_movies_data(self) -> List[Movies]:
        """Load data from sales and calendar table as training and validation data.

        Args:
            date_from (int): Starting date.
            date_to (int): Last date.

        Returns:
            List[SalesCalendar]: training and validation data.
        """

        data: List[Movies] = []
        position = 0
        limit = 10000
        while True:
            movies_data = self.movies_repository.select(
                # date_from=date_from,
                # date_to=date_to,
                limit=limit,
                offset=position,
            )
            if len(movies_data) == 0:
                break
            data.extend(movies_data)
            position += len(movies_data)
            logger.info(f"done loading {position}...")
        return data

    def load_ratings_data(self) -> List[Ratings]:
        """Load data from calendar table.

        Returns:
            List[Calendar]: calendar data.
        """

        data: List[Ratings] = []
        position = 0
        limit = 1000
        while True:
            ratings_data = self.ratings_repository.select(
                limit=limit,
                offset=position,
            )
            if len(ratings_data) == 0:
                break
            data.extend(ratings_data)
            position += len(ratings_data)
            logger.info(f"done loading {position}...")
        return data

    def load_tags_data(self) -> List[Tags]:
        """Load data from prices table.

        Returns:
            List[Prices]: prices data.
        """

        data: List[Tags] = []
        position = 0
        limit = 10000
        while True:
            tags_data = self.tags_repository.select(
                limit=limit,
                offset=position,
            )
            if len(tags_data) == 0:
                break
            data.extend(tags_data)
            position += len(tags_data)
            logger.info(f"done loading {position}...")
        return data
