from typing import List

import pandas as pd

from src.domain.model.raw_data import RawDataset
from src.domain.repository.movies_repository import AbstractMoviesRepository
from src.domain.repository.ratings_repository import AbstractRatingsRepository
from src.domain.repository.tags_repository import AbstractTagsRepository
from src.infrastructure.schema.movies_schema import Movies
from src.infrastructure.schema.ratings_schema import Ratings
from src.infrastructure.schema.tags_schema import Tags
from src.middleware.logger import configure_logger

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
            movies_repository (AbstractMoviesRepository): Repository to load data for movies.
            ratings_repository (AbstractRatingsRepository): Repository to load data for ratings.
            tags_repository  (AbstractTagsRepository): Repository to load data for tags.
        """

        self.movies_repository = movies_repository
        self.ratings_repository = ratings_repository
        self.tags_repository = tags_repository

    def load_dataset(self) -> RawDataset:
        """Load dataset for training and validation.

        Returns:
            RawDataset: Data loaded from database.
        """

        logger.info(f"load data from database")

        movies_df = self.make_movies_data()
        ratings_df = self.make_ratings_data()
        tags_df = self.make_tags_data()

        tags_df["tag"] = tags_df["tag"].str.lower()
        tags_agg_df = tags_df.groupby("movie_id").agg({"tag": list})
        movies_tags_df = movies_df.merge(tags_agg_df, on="movie_id", how="left")
        movies_tags_df["genre"] = movies_tags_df.genre.apply(lambda x: x.split("|"))
        logger.info(f"done dataload")
        logger.info(
            f"""load ratings:
{ratings_df}
        """
        )
        logger.info(
            f"""load movies_tags:
{movies_tags_df}
        """
        )
        return RawDataset(
            ratings_data=ratings_df,
            movies_tags_data=movies_tags_df,
        )

    def make_movies_data(self) -> pd.DataFrame:
        """make movies DataFrame.

        Returns:
            pd.DataFrame: movies data.
        """

        movies_data = self.load_movies_data()
        movies_dataset_dict = [d.model_dump() for d in movies_data]
        movies_df = pd.DataFrame(movies_dataset_dict)
        return movies_df

    def make_ratings_data(self) -> pd.DataFrame:
        """make ratings DataFrame.

        Returns:
            pd.DataFrame: ratings data.
        """

        ratings_data = self.load_ratings_data()
        ratings_dataset_dict = [d.model_dump() for d in ratings_data]
        ratings_df = pd.DataFrame(ratings_dataset_dict)
        return ratings_df

    def make_tags_data(self) -> pd.DataFrame:
        """make tags DataFrame.

        Returns:
            pd.DataFrame: tags data.
        """

        tags_data = self.load_tags_data()
        tags_dataset_dict = [d.model_dump() for d in tags_data]
        tags_df = pd.DataFrame(tags_dataset_dict)
        return tags_df

    def load_movies_data(self) -> List[Movies]:
        """Load data from movies table.

        Returns:
            List[Movies]: movies data.
        """

        data: List[Movies] = []
        position = 0
        limit = 10000
        while True:
            movies_data = self.movies_repository.select(
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
        """Load data from ratings table.

        Returns:
            List[Ratings]: ratings data.
        """

        data: List[Ratings] = []
        position = 0
        limit = 10000
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
        """Load data from tags table.

        Returns:
            List[Tags]: tags data.
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
