from dataclasses import dataclass

import pandas as pd
from pandera import Field, SchemaModel
from pandera.typing import Series



@dataclass(frozen=True)
class RawDataset:
    data_movielens: pd.DataFrame
    data_movies: pd.DataFrame

    def __post_init__(self):
        RawDataSchema.validate(self.data_movielens)

class RawDataSchema(SchemaModel):
    user_id: Series[str] = Field(
        nullable=False,
        coerce=True,
    )
    movie_id: Series[str] = Field(
        nullable=False,
        coerce=True,
    )
    rating: Series[float] = Field(
        ge=0.0,
        le=5.0,
        nullable=False,
        coerce=True,
    )
    timestamp: Series[int] = Field(
        ge=0,
        nullable=False,
        coerce=True,
    )
    title: Series[str] = Field(
        nullable=False,
        coerce=True,
    )
    genre: Series[str] = Field(
        nullable=False,
        coerce=True,
    )
    tag: Series[str] = Field(
        nullable=True,
        coerce=True,
    )

    class Config:
        name = "RawDataSchema"
        strict = True
        coerce = True
