from typing import Any, Dict, List, Optional, Tuple

import pytest

from src.infrastructure.database import AbstractDBClient
from src.repository.movies_repository import AbstractMoviesRepository
from src.repository.ratings_repository import AbstractRatingsRepository
from src.repository.tags_repository import AbstractTagsRepository
from src.schema.movies_schema import Movies
from src.schema.ratings_schema import Ratings
from src.schema.tags_schema import Tags


class MockPostgreSQLClient(AbstractDBClient):
    def __init__(self):
        super().__init__()

    def get_connection(self):
        pass

    def execute_create_query(
        self,
        query: str,
        parameters: Optional[Tuple] = None,
    ):
        pass

    def execute_bulk_insert_or_update_query(
        self,
        query: str,
        parameters: Optional[List[Tuple]] = None,
    ):
        pass

    def execute_select(
        self,
        query: str,
        parameters: Optional[Tuple] = None,
    ) -> List[Dict[str, Any]]:
        return []


class MockMoviesRepository(AbstractMoviesRepository):
    def __init__(
        self,
        db_client: AbstractDBClient,
    ):
        super().__init__(db_client=db_client)

    def select(
        self,
        limit: int = 200,
        offset: int = 0,
    ) -> List[Movies]:
        return []


class MockRatingsRepository(AbstractRatingsRepository):
    def __init__(
        self,
        db_client: AbstractDBClient,
    ):
        super().__init__(db_client=db_client)

    def select(
        self,
        limit: int = 200,
        offset: int = 0,
    ) -> List[Ratings]:
        return []


class MockTagsRepository(AbstractTagsRepository):
    def __init__(
        self,
        db_client: AbstractDBClient,
    ):
        super().__init__(db_client=db_client)

    def select(
        self,
        limit: int = 200,
        offset: int = 0,
    ) -> List[Tags]:
        return []


class Mocks(object):
    def __init__(self):
        self.db_client = MockPostgreSQLClient()
        self.movies_repository = MockMoviesRepository(db_client=self.db_client)
        self.ratings_repository = MockRatingsRepository(db_client=self.db_client)
        self.tags_repository = MockTagsRepository(db_client=self.db_client)


@pytest.fixture(scope="session", autouse=False)
def scope_session():
    yield


@pytest.fixture(scope="module", autouse=False)
def scope_module():
    yield


@pytest.fixture(scope="class", autouse=False)
def scope_class():
    mocks = Mocks()
    yield mocks
    mocks = None


@pytest.fixture(scope="function", autouse=False)
def scope_function():
    yield
