from abc import ABC, abstractmethod
from typing import List

from src.infrastructure.database.db_client import AbstractDBClient
from src.infrastructure.schema.ratings_schema import Ratings


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
