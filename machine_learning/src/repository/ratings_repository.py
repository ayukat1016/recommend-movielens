from abc import ABC, abstractmethod
from typing import List

from src.infrastructure.database import AbstractDBClient
from src.schema.ratings_schema import Ratings
from src.schema.tables_schema import TABLES


class AbstractRatingsRepository(ABC):
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
    ) -> List[Ratings]:
        raise NotImplementedError


class RatingsRepository(AbstractRatingsRepository):
    def __init__(
        self,
        db_client: AbstractDBClient,
    ):
        super().__init__(db_client=db_client)
        self.table_name = TABLES.RATINGS.value

    def select(
        self,
        limit: int = 200,
        offset: int = 0,
    ) -> List[Ratings]:
        query = f"""
        SELECT
            {self.table_name}.user_id as user_id,
            {self.table_name}.movie_id as movie_id,
            {self.table_name}.rating as rating,
            {self.table_name}.timestamp as timestamp
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
        data = [Ratings(**r) for r in records]
        return data
