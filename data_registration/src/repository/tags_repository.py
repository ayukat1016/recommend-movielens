from abc import ABC, abstractmethod
from typing import List

from src.infrastructure.database import AbstractDBClient
from src.schema.tables_schema import TABLES
from src.schema.tags_schema import Tags


class AbstractTagsRepository(ABC):
    def __init__(
        self,
        db_client: AbstractDBClient,
    ):
        self.db_client = db_client

    @abstractmethod
    def bulk_insert(
        self,
        records: List[Tags],
    ):
        raise NotImplementedError


class TagsRepository(AbstractTagsRepository):
    def __init__(
        self,
        db_client: AbstractDBClient,
    ):
        super().__init__(db_client=db_client)
        self.table_name = TABLES.TAGS.value

    def bulk_insert(
        self,
        records: List[Tags],
    ):
        data = records[0].model_dump()
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
            values = tuple(d.model_dump().values())
            parameters.append(values)
        self.db_client.execute_bulk_insert_or_update_query(
            query=query,
            parameters=parameters,
        )
