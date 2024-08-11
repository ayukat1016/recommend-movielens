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
    def bulk_insert(
        self,
        records: List[Ratings],
    ):
        raise NotImplementedError


class RatingsRepository(AbstractRatingsRepository):
    def __init__(
        self,
        db_client: AbstractDBClient,
    ):
        super().__init__(db_client=db_client)
        self.table_name = TABLES.RATINGS.value

    def bulk_insert(
        self,
        records: List[Ratings],
    ):
        data = records[0].dict()
        _columns = list(data.keys())
        columns = ",".join(_columns)
        query = f"""
        INSERT INTO
            {self.table_name}
            ({columns})
        VALUES
            %s
        ON CONFLICT
            (user_id, movie_id)
        DO NOTHING
        ;
        """

        parameters = []
        for d in records:
            values = tuple(d.dict().values())
            parameters.append(values)
        self.db_client.execute_bulk_insert_or_update_query(
            query=query,
            parameters=parameters,
        )
