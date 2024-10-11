from typing import List

from src.domain.repository.ratings_repository import AbstractRatingsRepository
from src.infrastructure.database.db_client import AbstractDBClient
from src.infrastructure.schema.ratings_schema import Ratings
from src.infrastructure.schema.tables_schema import TABLES


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
