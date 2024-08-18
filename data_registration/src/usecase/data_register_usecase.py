from src.middleware.file_reader import read_csv_to_list, read_text_file
from src.middleware.logger import configure_logger
from src.repository.movies_repository import AbstractMoviesRepository
from src.repository.ratings_repository import AbstractRatingsRepository
from src.repository.tables_repository import AbstractTablesRepository
from src.repository.tags_repository import AbstractTagsRepository
from src.schema.movies_schema import Movies
from src.schema.ratings_schema import Ratings
from src.schema.tags_schema import Tags

logger = configure_logger(__name__)


class DataRegisterUsecase(object):
    def __init__(
        self,
        tables_filepath: str,
        movies_filepath: str,
        ratings_filepath: str,
        tags_filepath: str,
        tables_repository: AbstractTablesRepository,
        movies_repository: AbstractMoviesRepository,
        ratings_repository: AbstractRatingsRepository,
        tags_repository: AbstractTagsRepository,
    ):
        self.tables_filepath = tables_filepath
        self.movies_filepath = movies_filepath
        self.ratings_filepath = ratings_filepath
        self.tags_filepath = tags_filepath
        self.tables_repository = tables_repository
        self.movies_repository = movies_repository
        self.ratings_repository = ratings_repository
        self.tags_repository = tags_repository

    def create_tables(self):
        query = read_text_file(file_path=self.tables_filepath)
        self.tables_repository.create_tables(query=query)

    def register_movies(self):
        data = read_csv_to_list(
            csv_file=self.movies_filepath,
            header=None,
            is_first_line_header=True,
        )
        limit = 10000
        i = 0
        records = []
        while i < len(data):
            d = data[i]
            records.append(
                Movies(
                    movie_id=d["movie_id"],
                    title=d["title"],
                    genre=d["genre"],
                )
            )
            i += 1
            if i % limit == 0:
                self.movies_repository.bulk_insert(records=records)
                logger.info(f"movies: {i} ...")
        if len(records) > 0:
            self.movies_repository.bulk_insert(records=records)
            logger.info(f"movies: {i} ...")

    def register_ratings(self):
        data = read_csv_to_list(
            csv_file=self.ratings_filepath,
            header=None,
            is_first_line_header=True,
        )
        limit = 10000
        i = 0
        records = []
        while i < len(data):
            d = data[i]
            records.append(
                Ratings(
                    user_id=d["user_id"],
                    movie_id=d["movie_id"],
                    rating=d["rating"],
                    timestamp=d["timestamp"],
                )
            )
            i += 1
            if i % limit == 0:
                self.ratings_repository.bulk_insert(records=records)
                logger.info(f"ratings: {i} ...")
        if len(records) > 0:
            self.ratings_repository.bulk_insert(records=records)
            logger.info(f"ratings: {i} ...")

    def register_tags(self):
        data = read_csv_to_list(
            csv_file=self.tags_filepath,
            header=None,
            is_first_line_header=True,
        )
        limit = 10000
        i = 0
        records = []
        while i < len(data):
            d = data[i]
            records.append(
                Tags(
                    user_id=d["user_id"],
                    movie_id=d["movie_id"],
                    tag=d["tag"],
                    timestamp=d["timestamp"],
                )
            )
            i += 1
            if i % limit == 0:
                self.tags_repository.bulk_insert(records=records)
                logger.info(f"tags: {i} ...")
        if len(records) > 0:
            self.tags_repository.bulk_insert(records=records)
            logger.info(f"tags: {i} ...")
