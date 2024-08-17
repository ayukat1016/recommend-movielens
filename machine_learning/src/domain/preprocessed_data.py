from dataclasses import dataclass

from pandera import Field, SchemaModel
from pandera.typing import Series

from src.domain.common_data import XY


class ExtractedRatingSchema(SchemaModel):
    u_min: Series[float] = Field(
        ge=0.0,
        le=5.0,
        nullable=True,
        coerce=True,
    )
    m_min: Series[float] = Field(
        ge=0.0,
        le=5.0,
        nullable=True,
        coerce=True,
    )
    u_max: Series[float] = Field(
        ge=0.0,
        le=5.0,
        nullable=True,
        coerce=True,
    )
    m_max: Series[float] = Field(
        ge=0.0,
        le=5.0,
        nullable=True,
        coerce=True,
    )
    u_mean: Series[float] = Field(
        ge=0.0,
        le=5.0,
        nullable=True,
        coerce=True,
    )
    m_mean: Series[float] = Field(
        ge=0.0,
        le=5.0,
        nullable=True,
        coerce=True,
    )

    class Config:
        name = "ExtractedRatingSchema"
        strict = True
        coerce = True


class ExtractedGenreSchema(SchemaModel):
    is_no_genres_listed: Series[bool] = Field(
        nullable=True,
        coerce=True,
    )
    is_Action: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Adventure: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Animation: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Children: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Comedy: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Crime: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Documentary: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Drama: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Fantasy: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Film_Noir: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Horror: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_IMAX: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Musical: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Mystery: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Romance: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Sci_Fi: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Thriller: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_War: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )
    is_Western: Series[bool] = Field(
        nullable=False,
        coerce=True,
    )

    class Config:
        name = "ExtractedGenreSchema"
        strict = True
        coerce = True


@dataclass(frozen=True)
class PreprocessedDataset:
    training_data: XY
    validation_data: XY
