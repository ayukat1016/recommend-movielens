from typing import Optional

import click

from src.infrastructure.database import PostgreSQLClient
from src.middleware.logger import configure_logger
from src.repository.movies_repository import MoviesRepository
from src.repository.ratings_repository import RatingsRepository
from src.repository.tables_repository import TablesRepository
from src.repository.tags_repository import TagsRepository
from src.usecase.data_register_usecase import DataRegisterUsecase

logger = configure_logger(__name__)


@click.command()
@click.option(
    "--tables_filepath",
    type=str,
    required=False,
)
@click.option(
    "--movies_filepath",
    type=str,
    required=False,
)
@click.option(
    "--ratings_filepath",
    type=str,
    required=False,
)
@click.option(
    "--tags_filepath",
    type=str,
    required=False,
)
def main(
    tables_filepath: Optional[str] = None,
    movies_filepath: Optional[str] = None,
    ratings_filepath: Optional[str] = None,
    tags_filepath: Optional[str] = None,
):

    if tables_filepath is None:
        raise ValueError("tables_filepath cannot be None")

    if movies_filepath is None:
        raise ValueError("movies_filepath cannot be None")

    if ratings_filepath is None:
        raise ValueError("ratinigs_filepath cannot be None")

    if tags_filepath is None:
        raise ValueError("tags_filepath cannot be None")

    logger.info("START data_registration")
    logger.info(
        f"""
options:
tables_filepath: {tables_filepath}
movies_filepath: {movies_filepath}
ratings_filepath: {ratings_filepath}
tags_filepath: {tags_filepath}
    """
    )
    db_client = PostgreSQLClient()
    tables_repository = TablesRepository(db_client=db_client)
    movies_repository = MoviesRepository(db_client=db_client)
    ratings_repository = RatingsRepository(db_client=db_client)
    tags_repository = TagsRepository(db_client=db_client)

    data_register_usecase = DataRegisterUsecase(
        tables_filepath=tables_filepath,
        movies_filepath=movies_filepath,
        ratings_filepath=ratings_filepath,
        tags_filepath=tags_filepath,
        tables_repository=tables_repository,
        movies_repository=movies_repository,
        ratings_repository=ratings_repository,
        tags_repository=tags_repository,
    )

    logger.info("create tables")
    data_register_usecase.create_tables()
    logger.info("done create tables")

    logger.info("register movies")
    data_register_usecase.register_movies()
    logger.info("done register movies")

    logger.info("register ratings")
    data_register_usecase.register_ratings()
    logger.info("done register ratings")

    logger.info("register tags")
    data_register_usecase.register_tags()
    logger.info("done register tags")

    logger.info("DONE data_registration")


if __name__ == "__main__":
    main()
