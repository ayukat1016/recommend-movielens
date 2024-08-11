from src.schema.abstract_schema import AbstractSchema


class Tags(AbstractSchema):
    user_id: int
    movie_id: int
    tag: str
    timestamp: int

    class Config:
        allow_mutations = False
        extra = "forbid"
