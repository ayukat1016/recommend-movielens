from abc import ABC, abstractmethod
from typing import List

from src.infrastructure.database import AbstractDBClient
from src.schema.movies_schema import Movies
from src.schema.tables_schema import TABLES


class AbstractMoviesRepository(ABC):
    def __init__(
        self,
        db_client: AbstractDBClient,
    ):
        self.db_client = db_client

    @abstractmethod
    def select(
        self,
        limit: int = 200,
        offset: int = 0,
    ) -> List[Movies]:
        raise NotImplementedError


class MoviesRepository(AbstractMoviesRepository):
    def __init__(
        self,
        db_client: AbstractDBClient,
    ):
        super().__init__(db_client=db_client)
        self.table_name = TABLES.MOVIES.value

    def select(
        self,
        limit: int = 200,
        offset: int = 0,
    ) -> List[Movies]:
        query = f"""
        SELECT
            {self.table_name}.movie_id as movie_id,
            {self.table_name}.title as title,
            {self.table_name}.genre as genre
        FROM
            {self.table_name}
        """

        query += f"""
        LIMIT
            {limit}
        OFFSET
            {offset}
        ;
        """
        records = self.db_client.execute_select(
            query=query,
        )
        data = [Movies(**r) for r in records]
        return data
