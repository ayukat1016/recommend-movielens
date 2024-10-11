from src.infrastructure.schema.abstract_schema import AbstractSchema


class Movies(AbstractSchema):
    movie_id: int
    title: str
    genre: str

    class Config:
        frozen = True
        extra = "forbid"
