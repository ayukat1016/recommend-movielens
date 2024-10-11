from typing import List

from src.domain.repository.movies_repository import AbstractMoviesRepository
from src.infrastructure.database.db_client import AbstractDBClient
from src.infrastructure.schema.movies_schema import Movies
from src.infrastructure.schema.tables_schema import TABLES


class MoviesRepository(AbstractMoviesRepository):
    def __init__(
        self,
        db_client: AbstractDBClient,
    ):
        super().__init__(db_client=db_client)
        self.table_name = TABLES.MOVIES.value

    def bulk_insert(
        self,
        records: List[Movies],
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
            (movie_id)
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
