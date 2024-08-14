import os

import mlflow  # type: ignore
from omegaconf import DictConfig

import hydra
# from src.domain.prediction_data import PredictionDataset
# from src.domain.training_data import TrainingDataset
from src.infrastructure.database import PostgreSQLClient
from src.middleware.logger import configure_logger
# from src.ml_algos.lightgbm_regressor import LightGBMRegression
# from src.ml_algos.models import get_model
# from src.ml_algos.preprocess import LagSalesExtractor, PricesExtractor
# from src.ml_algos.preprocess import RatingExtractor
from src.repository.movies_repository import MoviesRepository
from src.repository.ratings_repository import RatingsRepository
from src.repository.tags_repository import TagsRepository
# from src.repository.sales_calendar_repository import SalesCalendarRepository
from src.usecase.data_loader_usecase import DataLoaderUsecase
# from src.usecase.evaluation_usecase import EvaluationUsecase
# from src.usecase.prediction_register_usecase import PredictionRegisterUsecase
# from src.usecase.prediction_usecase import PredictionUsecase
from src.usecase.preprocess_usecase import PreprocessUsecase
# from src.usecase.training_usecase import TrainingUsecase

logger = configure_logger(__name__)


@hydra.main(
    config_path="/opt/hydra",
    config_name="default",
)
def main(cfg: DictConfig):
    logger.info("START machine_learning...")
    logger.info(f"config: {cfg}")
    cwd = os.getcwd()
    run_name = "-".join(cwd.split("/")[-2:])

    logger.info(f"current working directory: {cwd}")
    logger.info(f"run_name: {run_name}")
#     logger.info(
#         f"""parameters:
# training_date_from: {cfg.period.training_date_from}
# training_date_to: {cfg.period.training_date_to}
# validation_date_from: {cfg.period.validation_date_from}
# validation_date_to: {cfg.period.validation_date_to}
# prediction_date_from: {cfg.period.prediction_date_from}
# prediction_date_to: {cfg.period.prediction_date_to}
#     """
#     )

    # mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
    # mlflow.set_experiment(cfg.name)
    # with mlflow.start_run(run_name=run_name):

    #     mlflow.log_artifact(os.path.join(cwd, ".hydra/config.yaml"))
    #     mlflow.log_artifact(os.path.join(cwd, ".hydra/hydra.yaml"))
    #     mlflow.log_artifact(os.path.join(cwd, ".hydra/overrides.yaml"))

    #     mlflow.log_param("training_date_from", cfg.period.training_date_from)
    #     mlflow.log_param("training_date_to", cfg.period.training_date_to)
    #     mlflow.log_param("validation_date_from", cfg.period.validation_date_from)
    #     mlflow.log_param("validation_date_to", cfg.period.validation_date_to)
    #     mlflow.log_param("prediction_date_from", cfg.period.prediction_date_from)
    #     mlflow.log_param("prediction_date_to", cfg.period.prediction_date_to)

    db_client = PostgreSQLClient()
    movies_repository = MoviesRepository(db_client=db_client)
    ratings_repository = RatingsRepository(db_client=db_client)
    tags_repository = TagsRepository(db_client=db_client)

    data_loader_usecase = DataLoaderUsecase(
        movies_repository=movies_repository,
        ratings_repository=ratings_repository,
        tags_repository=tags_repository,
    )

    raw_dataset = data_loader_usecase.load_dataset(
        # training_date_from=cfg.period.training_date_from,
        # training_date_to=cfg.period.training_date_to,
        # validation_date_from=cfg.period.validation_date_from,
        # validation_date_to=cfg.period.validation_date_to,
        # prediction_date_from=cfg.period.prediction_date_from,
        # prediction_date_to=cfg.period.prediction_date_to,
    )

    # rating_extractor=RatingExtractor()


    preprocess_usecase = PreprocessUsecase(
        # rating_extractor=rating_extractor,
        # lag_sales_extractor=lag_sales_extractor,
    )

    preprocessed_dataset = preprocess_usecase.preprocess_dataset(
        dataset=raw_dataset
    )

    training_data_paths = preprocessed_dataset.training_data.save(
        directory=cwd, prefix=f"{run_name}_training_"
    )
    validation_data_paths = preprocessed_dataset.validation_data.save(
        directory=cwd, prefix=f"{run_name}_validation_"
    )
    # prediction_data_paths = preprocessed_dataset.prediction_data.save(
    #     directory=cwd, prefix=f"{run_name}_prediction_"
    # )
    logger.info(
        f"""save files
training data: {training_data_paths}
validation data: {validation_data_paths}
    """
    )

    train_x = preprocessed_dataset.training_data.x.copy()
    train_y = preprocessed_dataset.training_data.y.copy()
    test_x = preprocessed_dataset.validation_data.x.copy()
    test_y = preprocessed_dataset.validation_data.y.copy()

    movie_rating_predict = preprocessed_dataset.validation_data.keys.copy()


    # movielens_train = raw_dataset.data_train.data
    # movielens_test = raw_dataset.data_test.data
    # movies = raw_dataset.data_movies

    # # user_movie_matrix = movielens_train.pivot(index="user_id", columns="movie_id", values="rating")

    # train_keys = movielens_train[["user_id", "movie_id"]]
    # # train_y = movielens_train.rating.values
    # test_keys = movielens_test[["user_id", "movie_id"]]

    # train_x = train_keys.copy()
    # test_x = test_keys.copy()

    # # 学習用データに存在するユーザーごとの評価値の最小値、最大値、平均値
    # # 及び、映画ごとの評価値の最小値、最大値、平均値を特徴量として追加
    # aggregators = ["min", "max", "mean"]
    # user_features = movielens_train.groupby("user_id").rating.agg(aggregators).to_dict()
    # movie_features = movielens_train.groupby("movie_id").rating.agg(aggregators).to_dict()
    # for agg in aggregators:
    #     train_x[f"u_{agg}"] = train_x["user_id"].map(user_features[agg])
    #     test_x[f"u_{agg}"] = test_x["user_id"].map(user_features[agg])
    #     # train_all_x[f"u_{agg}"] = train_all_x["user_id"].map(user_features[agg])
    #     train_x[f"m_{agg}"] = train_x["movie_id"].map(movie_features[agg])
    #     test_x[f"m_{agg}"] = test_x["movie_id"].map(movie_features[agg])
    #     # train_all_x[f"m_{agg}"] = train_all_x["movie_id"].map(movie_features[agg])
    # # テスト用データにしか存在しないユーザーや映画の特徴量を、学習用データ全体の平均評価値で埋める
    # average_rating = train_y.mean()
    # test_x.fillna(average_rating, inplace=True)

    # import itertools

    # # 映画が特定の genre であるかどうかを表す特徴量を追加
    # movie_genres = movies[["movie_id", "genre"]].copy()

    # import ast

    # # 各ジャンルをリストに戻す
    # movie_genres["genre"] = movie_genres["genre"].apply(ast.literal_eval)
    # genres = set(list(itertools.chain(*movie_genres.genre)))
    # # print(genres)
    # genres = sorted(genres)
    # # genres = genres.sort_values(by=["genre"]).reset_index(drop=True)
    # print(genres)

    # for genre in genres:
    #     # print(genre)
    #     movie_genres.loc[:, f"is_{genre}"] = movie_genres.genre.apply(lambda x: genre in x)
    # movie_genres.drop("genre", axis=1, inplace=True)
    # train_x = train_x.merge(movie_genres, on="movie_id")
    # test_x = test_x.merge(movie_genres, on="movie_id")
    # # train_all_x = train_all_x.merge(movie_genres, on="movie_id")

    # print(train_x)
    # print(test_x)

    from sklearn.ensemble import RandomForestRegressor as RFR

    # Random Forest を用いた学習
    reg = RFR(n_jobs=-1, random_state=0)
    reg.fit(train_x.values, train_y)

    # テスト用データ内のユーザーと映画の組に対して評価値を予測する
    test_pred = reg.predict(test_x.values)

    # movie_rating_predict = test_keys.copy()
    movie_rating_predict["rating_pred"] = test_pred

    print(movie_rating_predict)



#     prices_extractor = PricesExtractor()
#     lag_sales_extractor = LagSalesExtractor()
#     preprocess_usecase = PreprocessUsecase(
#         prices_extractor=prices_extractor,
#         lag_sales_extractor=lag_sales_extractor,
#     )

#     preprocessed_dataset = preprocess_usecase.preprocess_dataset(
#         dataset=raw_dataset
#     )

#     training_data_paths = preprocessed_dataset.training_data.save(
#         directory=cwd, prefix=f"{run_name}_training_"
#     )
#     validation_data_paths = preprocessed_dataset.validation_data.save(
#         directory=cwd, prefix=f"{run_name}_validation_"
#     )
#     prediction_data_paths = preprocessed_dataset.prediction_data.save(
#         directory=cwd, prefix=f"{run_name}_prediction_"
#     )
#     logger.info(
#         f"""save files
# training data: {training_data_paths}
# validation data: {validation_data_paths}
# prediction data: {prediction_data_paths}
#     """
#     )

#     mlflow.log_artifact(training_data_paths[0], "training_xy_keys")
#     mlflow.log_artifact(training_data_paths[1], "training_xy_x")
#     mlflow.log_artifact(training_data_paths[2], "training_xy_y")
#     mlflow.log_artifact(validation_data_paths[0], "validation_xy_keys")
#     mlflow.log_artifact(validation_data_paths[1], "validation_xy_x")
#     mlflow.log_artifact(validation_data_paths[2], "validation_xy_y")
#     mlflow.log_artifact(prediction_data_paths[0], "prediction_xy_keys")
#     mlflow.log_artifact(prediction_data_paths[1], "prediction_xy_x")
#     mlflow.log_artifact(prediction_data_paths[2], "prediction_xy_y")

#     for col in [
#         "item_id",
#         "dept_id",
#         "event_name_1",
#         "event_type_1",
#         "event_name_2",
#         "event_type_2",
#     ]:
#         preprocessed_dataset.training_data.x[col] = (
#             preprocessed_dataset.training_data.x[col].astype("category")
#         )
#         preprocessed_dataset.validation_data.x[col] = (
#             preprocessed_dataset.validation_data.x[col].astype("category")
#         )
#         preprocessed_dataset.prediction_data.x[col] = (
#             preprocessed_dataset.prediction_data.x[col].astype("category")
#         )

#     logger.info(
#         f"""loaded preprocessed dataset:
# training:
# {preprocessed_dataset.training_data}
# validation:
# {preprocessed_dataset.validation_data}
# prediction:
# {preprocessed_dataset.prediction_data}
#             """
#     )

#     model_class = get_model(model=cfg.model.name)
#     model = model_class()
#     if isinstance(model, LightGBMRegression):
#         model.reset_model(
#             params=cfg.model.params,
#             train_params=cfg.model.train_params,
#         )
#     mlflow.log_param("model", cfg.model.name)
#     mlflow.log_params(model.params)

#     training_usecase = TrainingUsecase()
#     prediction_usecase = PredictionUsecase()
#     evaluation_usecase = EvaluationUsecase()

#     prediction_repository = PredictionRepository(db_client=db_client)
#     prediction_register_usecase = PredictionRegisterUsecase(
#         prediction_repository=prediction_repository,
#     )

#     for store_id in sorted(
#         list(preprocessed_dataset.training_data.keys["store_id"].unique())
#     ):

#         logger.info(f"START machine learning task for {store_id}")

#         train_store_mask = (
#             preprocessed_dataset.training_data.keys["store_id"] == store_id
#         )
#         valid_store_mask = (
#             preprocessed_dataset.validation_data.keys["store_id"] == store_id
#         )
#         preds_store_mask = (
#             preprocessed_dataset.prediction_data.keys["store_id"] == store_id
#         )

#         training_dataset = TrainingDataset(
#             training_data=preprocessed_dataset.training_data,
#             validation_data=preprocessed_dataset.validation_data,
#         )

#         training_usecase.train(
#             model=model,
#             training_data=training_dataset,
#             train_mask=train_store_mask,
#             valid_mask=valid_store_mask,
#         )

#         validation_prediction_dataset = PredictionDataset(
#             prediction_data=preprocessed_dataset.validation_data
#         )
#         validation_prediction = prediction_usecase.predict(
#             model=model,
#             data=validation_prediction_dataset,
#             mask=valid_store_mask,
#         )

#         evaluation = evaluation_usecase.evaluate(
#             date_id=validation_prediction.prediction.date_id.tolist(),
#             store_id=validation_prediction.prediction.store_id.tolist(),
#             item_id=validation_prediction.prediction.item_id.tolist(),
#             y_true=preprocessed_dataset.validation_data.y[
#                 valid_store_mask
#             ].sales.tolist(),
#             y_pred=validation_prediction.prediction.prediction.tolist(),
#         )

#         feature_importance = evaluation_usecase.export_feature_importance(
#             model=model
#         )

#         prediction_dataset = PredictionDataset(
#             prediction_data=preprocessed_dataset.prediction_data
#         )
#         prediction_output = prediction_usecase.predict(
#             model=model,
#             data=prediction_dataset,
#             mask=preds_store_mask,
#         )

#         predictions = prediction_output.prediction

#         prediction_register_usecase.register_prediction(
#             predictions=predictions,
#         )

#         base_file_name = f"{run_name}"
#         model_file_path = os.path.join(
#             cwd, f"{base_file_name}_{store_id}_model.txt"
#         )
#         model_file_path = model.save(file_path=model_file_path)
#         evaluation_file_path = os.path.join(
#             cwd, f"{base_file_name}_{store_id}_evaluation.csv"
#         )
#         evaluation_file_path = evaluation.save_data(file_path=evaluation_file_path)
#         feature_importance_file_path = os.path.join(
#             cwd, f"{base_file_name}_{store_id}_feature_importance.csv"
#         )
#         feature_importance_file_path = feature_importance.save(
#             file_path=feature_importance_file_path
#         )
#         prediction_file_path = os.path.join(
#             cwd, f"{base_file_name}_{store_id}_prediction.csv"
#         )
#         prediction_file_path = prediction_output.save(
#             file_path=prediction_file_path
#         )

#         mlflow.log_artifact(model_file_path, "model")
#         mlflow.log_artifact(evaluation_file_path, "evaluation")
#         mlflow.log_artifact(feature_importance_file_path, "feature_importance")
#         mlflow.log_artifact(prediction_file_path, "prediction")
#         mlflow.log_metric(
#             f"{store_id}_mean_absolute_error", evaluation.mean_absolute_error
#         )
#         mlflow.log_metric(
#             f"{store_id}_root_mean_squared_error",
#             evaluation.root_mean_squared_error,
#         )

#         logger.info(f"DONE machine learning task for {store_id}")

#         logger.info(f"DONE machine learning task for {cfg.model.name}: {run_name}")

    logger.info("DONE machine_learning")


if __name__ == "__main__":
    main()
