from abc import ABC, abstractmethod
from typing import List

from src.infrastructure.database.db_client import AbstractDBClient
from src.infrastructure.schema.tags_schema import Tags


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

