from src.schema.abstract_schema import AbstractSchema


class Movies(AbstractSchema):
    movie_id: int
    title: str
    genre: str

    class Config:
        allow_mutations = False
        extra = "forbid"
