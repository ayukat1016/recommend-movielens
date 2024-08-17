import os
from dataclasses import dataclass

import pandas as pd
from pandera import Field, SchemaModel
from pandera.typing import Series
from pydantic import BaseModel


@dataclass(frozen=True)
class Evaluation:
    data: pd.DataFrame
    root_mean_squared_error: float
    mean_absolute_error: float

    def __post_init__(self):
        EvaluationDataSchema.validate(self.data)

    def save_data(
        self,
        file_path: str,
    ) -> str:
        _, ext = os.path.splitext(file_path)
        if ext != ".csv":
            file_path += ".csv"
        self.data.to_csv(file_path, index=False)
        return file_path


class EvaluationDataSchema(SchemaModel):
    user_id: Series[str] = Field(
        nullable=False,
        coerce=True,
    )
    recency_id: Series[str] = Field(
        nullable=False,
        coerce=True,
    )
    movie_id: Series[str] = Field(
        nullable=False,
        coerce=True,
    )
    y_true: Series[float] = Field(
        ge=0.0,
        le=5.0,
        nullable=False,
        coerce=True,
    )
    y_pred: Series[float] = Field(
        ge=0.0,
        le=5.0,
        nullable=False,
        coerce=True,
    )

    class Config:
        name = "EvaluationDataSchema"
        strict = True
        coerce = True


class FeatureImportance(BaseModel):
    feature_name: str
    importance: float

    class Config:
        allow_mutation = False


@dataclass(frozen=True)
class FeatureImportances:
    feature_importances: pd.DataFrame

    def save(
        self,
        file_path: str,
    ) -> str:
        _, ext = os.path.splitext(file_path)
        if ext != ".csv":
            file_path += ".csv"
        self.feature_importances.to_csv(file_path, index=False)
        return file_path
