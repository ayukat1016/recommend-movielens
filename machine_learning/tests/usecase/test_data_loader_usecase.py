import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.domain.raw_data import RawDataMoviesSchema
from src.domain.raw_data import RawDataRatingsSchema
from src.domain.raw_data import RawDataTagsSchema
from src.schema.movies_schema import Movies
from src.schema.ratings_schema import Ratings
from src.schema.tags_schema import Tags
from src.usecase.data_loader_usecase import DataLoaderUsecase


@pytest.mark.usefixtures("scope_class")
@pytest.mark.parametrize(
    (
        "movies_data",
        "ratings_data",
        "tags_data",
    ),
    [
        (
            [
                Movies(
                    movie_id=1,
                    title="a",
                    genre="aa",
                ),
                Movies(
                    movie_id=2,
                    title="b",
                    genre="bb",
                ),
                Movies(
                    movie_id=3,
                    title="c",
                    genre="cc",
                ),
            ],
            [
                Ratings(
                    user_id=1,
                    movie_id=1,
                    rating=1.0,
                    timestamp=1,
                ),
                Ratings(
                    user_id=2,
                    movie_id=2,
                    rating=2.0,
                    timestamp=2,
                ),
                Ratings(
                    user_id=3,
                    movie_id=3,
                    rating=3.0,
                    timestamp=3,
                ),
            ],
            [
                Tags(
                    user_id=1,
                    movie_id=1,
                    tag="a",
                    timestamp=1,
                ),
                Tags(
                    user_id=2,
                    movie_id=2,
                    tag="b",
                    timestamp=2,
                ),
                Tags(
                    user_id=3,
                    movie_id=3,
                    tag="c",
                    timestamp=3,
                ),
            ],
        )
    ],
)
def test_load_data(
    mocker,
    scope_class,
    movies_data,
    ratings_data,
    tags_data,
):
    data_loader_usecase = DataLoaderUsecase(
        movies_repository=scope_class.movies_repository,
        ratings_repository=scope_class.ratings_repository,
        tags_repository=scope_class.tags_repository,
    )

    mocker.patch.object(
        data_loader_usecase, "load_movies_data", return_value=movies_data
    )
    mocker.patch.object(
        data_loader_usecase, "load_ratings_data", return_value=ratings_data
    )
    mocker.patch.object(data_loader_usecase, "load_tags_data", return_value=tags_data)

    got_movies = data_loader_usecase.make_movies_data()
    want_movies = pd.DataFrame([d.model_dump() for d in movies_data])
    assert_frame_equal(got_movies, want_movies)
    RawDataMoviesSchema.validate(got_movies)

    got_ratings = data_loader_usecase.make_ratings_data()
    want_ratings = pd.DataFrame([d.model_dump() for d in ratings_data])
    assert_frame_equal(got_ratings, want_ratings)
    RawDataRatingsSchema.validate(got_ratings)

    got_tags = data_loader_usecase.make_tags_data()
    want_tags = pd.DataFrame([d.model_dump() for d in tags_data])
    assert_frame_equal(got_tags, want_tags)
    RawDataTagsSchema.validate(got_tags)
