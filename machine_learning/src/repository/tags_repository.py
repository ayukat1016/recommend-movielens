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
    def select(
        self,
        limit: int = 200,
        offset: int = 0,
    ) -> List[Tags]:
        raise NotImplementedError


class TagsRepository(AbstractTagsRepository):
    def __init__(
        self,
        db_client: AbstractDBClient,
    ):
        super().__init__(db_client=db_client)
        self.table_name = TABLES.TAGS.value

    def select(
        self,
        limit: int = 200,
        offset: int = 0,
    ) -> List[Tags]:
        query = f"""
        SELECT
            {self.table_name}.user_id as user_id,
            {self.table_name}.movie_id as movie_id,
            {self.table_name}.tag as tag,
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
        data = [Tags(**r) for r in records]
        return data
