from src.infrastructure.schema.abstract_schema import AbstractSchema


class Tags(AbstractSchema):
    user_id: int
    movie_id: int
    tag: str
    timestamp: int

    class Config:
        frozen = True
        extra = "forbid"
