import os
from dataclasses import dataclass

import pandas as pd
from pandera import Field, SchemaModel
from pandera.typing import Series

from src.domain.common_data import XY


@dataclass(frozen=True)
class PredictionDataset:
    prediction_data: XY


@dataclass(frozen=True)
class Prediction:
    data: pd.DataFrame

    def __post_init__(self):
        PredictionDataSchema.validate(self.data)

    def save(
        self,
        file_path: str,
    ) -> str:
        _, ext = os.path.splitext(file_path)
        if ext != ".csv":
            file_path += ".csv"
        self.data.to_csv(file_path, index=False)
        return file_path


class PredictionDataSchema(SchemaModel):
    user_id: Series[int] = Field(
        nullable=False,
        coerce=True,
    )
    timestamp_rank: Series[int] = Field(
        nullable=False,
        coerce=True,
    )
    movie_id: Series[int] = Field(
        nullable=False,
        coerce=True,
    )
    prediction: Series[float] = Field(
        ge=0.5,
        le=5.0,
        nullable=False,
        coerce=True,
    )

    class Config:
        name = "PredictionDataSchema"
        strict = True
        coerce = True


@dataclass(frozen=True)
class Recommendation:
    data: pd.DataFrame

    def __post_init__(self):
        RecommendationDataSchema.validate(self.data)

    def save(
        self,
        file_path: str,
    ) -> str:
        _, ext = os.path.splitext(file_path)
        if ext != ".csv":
            file_path += ".csv"
        self.data.to_csv(file_path, index=False)
        return file_path


class RecommendationDataSchema(SchemaModel):
    user_id: Series[int] = Field(
        nullable=False,
        coerce=True,
    )
    movie_id: Series[int] = Field(
        nullable=False,
        coerce=True,
    )
    prediction: Series[float] = Field(
        ge=0.5,
        le=5.0,
        nullable=False,
        coerce=True,
    )

    class Config:
        name = "RecommendationDataSchema"
        strict = True
        coerce = True
