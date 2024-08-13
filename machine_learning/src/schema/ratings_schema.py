from src.schema.abstract_schema import AbstractSchema


class Ratings(AbstractSchema):
    user_id: int
    movie_id: int
    rating: float
    timestamp: int

    class Config:
        allow_mutations = False
        extra = "forbid"
