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
        df1: pd.DataFrame,
        df2: pd.DataFrame,
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
        df_rating = df[["user_id", "rank_id", "movie_id", "rating"]].copy()
        aggregators: list = ["min", "max", "mean"]
        user_features = movielens_train.groupby("user_id").rating.agg(aggregators).to_dict()
        movie_features = movielens_train.groupby("movie_id").rating.agg(aggregators).to_dict()
        for agg in aggregators:
            df_rating[f"u_{agg}"] = df_rating["user_id"].map(user_features[agg])
            df_rating[f"m_{agg}"] = df_rating["movie_id"].map(movie_features[agg])

        df = df_rating.iloc[:, 4:]

        ExtractedRatingSchema.validate(df)
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
        df_genre = df[["user_id", "rank_id", "movie_id", "rating"]].copy()        
        movie_genres = movies[["movie_id", "genre"]].copy()
        movie_genres["genre"] = movie_genres["genre"].apply(ast.literal_eval)
        genres = list(set(itertools.chain(*movie_genres.genre)))
        genres = sorted(genres)

        for genre in genres:
            movie_genres.loc[:, f"is_{genre}"] = movie_genres.genre.apply(lambda x: genre in x)
        movie_genres.drop("genre", axis=1, inplace=True)
        df_genre = df_genre.merge(movie_genres, on="movie_id")

        df_genre = df_genre.rename(columns={"is_(no genres listed)": "is_no_genres_listed"})
        df_genre = df_genre.rename(columns={"is_Film-Noir": "is_Film_Noir"})
        df_genre = df_genre.rename(columns={"is_Sci-Fi": "is_Sci_Fi"})

        df = df_genre.iloc[:, 4:]

        ExtractedGenreSchema.validate(df)
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
