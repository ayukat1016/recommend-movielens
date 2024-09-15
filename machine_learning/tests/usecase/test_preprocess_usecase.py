import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from src.ml_algos.preprocess import RatingsExtractor, GenreExtractor
from src.domain.common_data import XY
from src.usecase.preprocess_usecase import PreprocessUsecase


@pytest.mark.usefixtures("scope_function")
@pytest.mark.parametrize(
    (
        "keys",
        "data",
        "want",
    ),
    [
        (
            pd.DataFrame(
                [
                    dict(user_id=1, timestamp_rank=1, movie_id=1),
                    dict(user_id=2, timestamp_rank=2, movie_id=2),
                    dict(user_id=3, timestamp_rank=3, movie_id=3),
                ]
            ),
            pd.DataFrame(
                [
                    {
                        "rating": 1.0,
                        "u_min": 1.0,
                        "m_min": 1.0,
                        "u_max": 1.0,
                        "m_max": 1.0,
                        "u_mean": 1.0,
                        "m_mean": 1.0,
                        "is_no_genres_listed": True,
                        "is_Action": False,
                        "is_Adventure": False,
                        "is_Animation": False,
                        "is_Children": False,
                        "is_Comedy": False,
                        "is_Crime": False,
                        "is_Documentary": False,
                        "is_Drama": False,
                        "is_Fantasy": False,
                        "is_Film_Noir": False,
                        "is_Horror": False,
                        "is_IMAX": False,
                        "is_Musical": False,
                        "is_Mystery": False,
                        "is_Romance": False,
                        "is_Sci_Fi": False,
                        "is_Thriller": False,
                        "is_War": False,
                        "is_Western": False,
                    },
                    {
                        "rating": 2.0,
                        "u_min": 2.0,
                        "m_min": 2.0,
                        "u_max": 2.0,
                        "m_max": 2.0,
                        "u_mean": 2.0,
                        "m_mean": 2.0,
                        "is_no_genres_listed": False,
                        "is_Action": True,
                        "is_Adventure": False,
                        "is_Animation": False,
                        "is_Children": False,
                        "is_Comedy": False,
                        "is_Crime": False,
                        "is_Documentary": False,
                        "is_Drama": False,
                        "is_Fantasy": False,
                        "is_Film_Noir": False,
                        "is_Horror": False,
                        "is_IMAX": False,
                        "is_Musical": False,
                        "is_Mystery": False,
                        "is_Romance": False,
                        "is_Sci_Fi": False,
                        "is_Thriller": False,
                        "is_War": False,
                        "is_Western": False,
                    },
                    {
                        "rating": 3.0,
                        "u_min": 3.0,
                        "m_min": 3.0,
                        "u_max": 3.0,
                        "m_max": 3.0,
                        "u_mean": 3.0,
                        "m_mean": 3.0,
                        "is_no_genres_listed": False,
                        "is_Action": False,
                        "is_Adventure": True,
                        "is_Animation": False,
                        "is_Children": False,
                        "is_Comedy": False,
                        "is_Crime": False,
                        "is_Documentary": False,
                        "is_Drama": False,
                        "is_Fantasy": False,
                        "is_Film_Noir": False,
                        "is_Horror": False,
                        "is_IMAX": False,
                        "is_Musical": False,
                        "is_Mystery": False,
                        "is_Romance": False,
                        "is_Sci_Fi": False,
                        "is_Thriller": False,
                        "is_War": False,
                        "is_Western": False,
                    },
                ]
            ),
            XY(
                keys=pd.DataFrame(
                    [
                    dict(user_id=1, timestamp_rank=1, movie_id=1),
                    dict(user_id=2, timestamp_rank=2, movie_id=2),
                    dict(user_id=3, timestamp_rank=3, movie_id=3),
                    ]
                ),
                x=pd.DataFrame(
                    [
                        {
                            "u_min": 1.0,
                            "m_min": 1.0,
                            "u_max": 1.0,
                            "m_max": 1.0,
                            "u_mean": 1.0,
                            "m_mean": 1.0,
                            "is_no_genres_listed": True,
                            "is_Action": False,
                            "is_Adventure": False,
                            "is_Animation": False,
                            "is_Children": False,
                            "is_Comedy": False,
                            "is_Crime": False,
                            "is_Documentary": False,
                            "is_Drama": False,
                            "is_Fantasy": False,
                            "is_Film_Noir": False,
                            "is_Horror": False,
                            "is_IMAX": False,
                            "is_Musical": False,
                            "is_Mystery": False,
                            "is_Romance": False,
                            "is_Sci_Fi": False,
                            "is_Thriller": False,
                            "is_War": False,
                            "is_Western": False,
                        },
                        {
                            "u_min": 2.0,
                            "m_min": 2.0,
                            "u_max": 2.0,
                            "m_max": 2.0,
                            "u_mean": 2.0,
                            "m_mean": 2.0,
                            "is_no_genres_listed": False,
                            "is_Action": True,
                            "is_Adventure": False,
                            "is_Animation": False,
                            "is_Children": False,
                            "is_Comedy": False,
                            "is_Crime": False,
                            "is_Documentary": False,
                            "is_Drama": False,
                            "is_Fantasy": False,
                            "is_Film_Noir": False,
                            "is_Horror": False,
                            "is_IMAX": False,
                            "is_Musical": False,
                            "is_Mystery": False,
                            "is_Romance": False,
                            "is_Sci_Fi": False,
                            "is_Thriller": False,
                            "is_War": False,
                            "is_Western": False,
                        },
                        {
                            "u_min": 3.0,
                            "m_min": 3.0,
                            "u_max": 3.0,
                            "m_max": 3.0,
                            "u_mean": 3.0,
                            "m_mean": 3.0,
                            "is_no_genres_listed": False,
                            "is_Action": False,
                            "is_Adventure": True,
                            "is_Animation": False,
                            "is_Children": False,
                            "is_Comedy": False,
                            "is_Crime": False,
                            "is_Documentary": False,
                            "is_Drama": False,
                            "is_Fantasy": False,
                            "is_Film_Noir": False,
                            "is_Horror": False,
                            "is_IMAX": False,
                            "is_Musical": False,
                            "is_Mystery": False,
                            "is_Romance": False,
                            "is_Sci_Fi": False,
                            "is_Thriller": False,
                            "is_War": False,
                            "is_Western": False,
                        },
                    ]
                ),
                y=pd.DataFrame(
                    [
                        dict(rating=1.0),
                        dict(rating=2.0),
                        dict(rating=3.0)
                    ]
                ),
            ),
        )
    ],
)
def test_split_data_target(
    mocker,
    scope_function,
    keys,
    data,
    want,
):
    ratings_extractor = RatingsExtractor()
    genre_extractor = GenreExtractor()
    preprocess_usecase = PreprocessUsecase(
        ratings_extractor=ratings_extractor,
        genre_extractor=genre_extractor,
    )
    got = preprocess_usecase.split_data_target(
        keys=keys,
        data=data,
    )
    assert_frame_equal(got.keys, want.keys)
    assert_frame_equal(got.x, want.x)
    assert_frame_equal(got.y, want.y)

