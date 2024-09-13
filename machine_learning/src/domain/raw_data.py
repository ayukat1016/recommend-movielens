from dataclasses import dataclass

import pandas as pd
from pandera import Field, SchemaModel
from pandera.typing import Series


@dataclass(frozen=True)
class RawDataset:
    ratings_data: pd.DataFrame
    movies_tags_data: pd.DataFrame

    def __post_init__(self):
        RawDataRatingsSchema.validate(self.ratings_data)
        RawDataMoviesTagsSchema.validate(self.movies_tags_data)


class RawDataRatingsSchema(SchemaModel):
    user_id: Series[int] = Field(
        nullable=False,
        coerce=True,
    )
    movie_id: Series[int] = Field(
        nullable=False,
        coerce=True,
    )
    rating: Series[float] = Field(
        ge=0.5,
        le=5.0,
        nullable=False,
        coerce=True,
    )
    timestamp: Series[int] = Field(
        ge=0,
        nullable=False,
        coerce=True,
    )

    class Config:
        name = "RawDataRatingsSchema"
        strict = True
        coerce = True


class RawDataMoviesTagsSchema(SchemaModel):
    movie_id: Series[int] = Field(
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
        name = "RawDataMoviesTagsSchema"
        strict = True
        coerce = True


class RawDataMoviesSchema(SchemaModel):
    movie_id: Series[int] = Field(
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

    class Config:
        name = "RawDataMoviesSchema"
        strict = True
        coerce = True


class RawDataTagsSchema(SchemaModel):
    user_id: Series[int] = Field(
        nullable=False,
        coerce=True,
    )
    movie_id: Series[int] = Field(
        nullable=False,
        coerce=True,
    )
    tag: Series[str] = Field(
        nullable=True,
        coerce=True,
    )
    timestamp: Series[int] = Field(
        ge=0,
        nullable=False,
        coerce=True,
    )

    class Config:
        name = "RawDataRatingsSchema"
        strict = True
        coerce = True
