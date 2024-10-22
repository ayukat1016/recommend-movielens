import os

import mlflow  # type: ignore
from omegaconf import DictConfig

import hydra
from src.domain.algorithm.lightgbm_regressor import LightGBMRegression
from src.domain.algorithm.models import get_model
from src.domain.algorithm.preprocess import GenreExtractor, RatingsExtractor
from src.domain.model.prediction_data import PredictionDataset
from src.domain.model.training_data import TrainingDataset
from src.infrastructure.database.db_client import PostgreSQLClient
from src.infrastructure.repository.movies_repository import MoviesRepository
from src.infrastructure.repository.ratings_repository import RatingsRepository
from src.infrastructure.repository.tags_repository import TagsRepository
from src.middleware.logger import configure_logger
from src.usecase.data_loader_usecase import DataLoaderUsecase
from src.usecase.evaluation_usecase import EvaluationUsecase
from src.usecase.prediction_usecase import PredictionUsecase
from src.usecase.preprocess_usecase import PreprocessUsecase
from src.usecase.training_usecase import TrainingUsecase

logger = configure_logger(__name__)


@hydra.main(
    version_base="1.1",
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
    logger.info(
        f"""parameters:
    validation_records: {cfg.period.validation.user_recency_records}
        """
    )

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
    mlflow.set_experiment(cfg.name)
    with mlflow.start_run(run_name=run_name):

        mlflow.log_artifact(os.path.join(cwd, ".hydra/config.yaml"))
        mlflow.log_artifact(os.path.join(cwd, ".hydra/hydra.yaml"))
        mlflow.log_artifact(os.path.join(cwd, ".hydra/overrides.yaml"))

        mlflow.log_param(
            "validation_records", cfg.period.validation.user_recency_records
        )

        db_client = PostgreSQLClient()
        movies_repository = MoviesRepository(db_client=db_client)
        ratings_repository = RatingsRepository(db_client=db_client)
        tags_repository = TagsRepository(db_client=db_client)

        data_loader_usecase = DataLoaderUsecase(
            movies_repository=movies_repository,
            ratings_repository=ratings_repository,
            tags_repository=tags_repository,
        )

        raw_dataset = data_loader_usecase.load_dataset()

        ratings_extractor = RatingsExtractor()
        genre_extractor = GenreExtractor()

        preprocess_usecase = PreprocessUsecase(
            ratings_extractor=ratings_extractor,
            genre_extractor=genre_extractor,
        )

        preprocessed_dataset = preprocess_usecase.preprocess_dataset(
            dataset=raw_dataset,
            validation_records=cfg.period.validation.user_recency_records,
        )

        training_data_paths = preprocessed_dataset.training_data.save(
            directory=cwd, prefix=f"{run_name}_training_"
        )
        validation_data_paths = preprocessed_dataset.validation_data.save(
            directory=cwd, prefix=f"{run_name}_validation_"
        )
        logger.info(
            f"""save files
    training data: {training_data_paths}
    validation data: {validation_data_paths}
        """
        )

        mlflow.log_artifact(training_data_paths[0], "training_xy_keys")
        mlflow.log_artifact(training_data_paths[1], "training_xy_x")
        mlflow.log_artifact(training_data_paths[2], "training_xy_y")
        mlflow.log_artifact(validation_data_paths[0], "validation_xy_keys")
        mlflow.log_artifact(validation_data_paths[1], "validation_xy_x")
        mlflow.log_artifact(validation_data_paths[2], "validation_xy_y")

        model_class = get_model(model=cfg.model.name)
        model = model_class()
        if isinstance(model, LightGBMRegression):
            model.reset_model(
                params=cfg.model.params,
                train_params=cfg.model.train_params,
            )

        mlflow.log_param("model", cfg.model.name)
        mlflow.log_params(model.params)

        training_usecase = TrainingUsecase()

        training_dataset = TrainingDataset(
            training_data=preprocessed_dataset.training_data,
            validation_data=preprocessed_dataset.validation_data,
        )

        training_usecase.train(
            model=model,
            training_data=training_dataset,
        )

        prediction_usecase = PredictionUsecase()

        validation_prediction_dataset = PredictionDataset(
            prediction_data=preprocessed_dataset.validation_data
        )

        validation_prediction = prediction_usecase.predict(
            model=model,
            data=validation_prediction_dataset,
        )

        evaluation_usecase = EvaluationUsecase()

        evaluation = evaluation_usecase.evaluate(
            user_id=validation_prediction.data.user_id.tolist(),
            timestamp_rank=validation_prediction.data.timestamp_rank.tolist(),
            movie_id=validation_prediction.data.movie_id.tolist(),
            y_pred=validation_prediction.data.prediction.tolist(),
            y_true=preprocessed_dataset.validation_data.y.rating.tolist(),
        )

        feature_importance = evaluation_usecase.export_feature_importance(model=model)

        validation_recommendation = prediction_usecase.recommend(
            model=model,
            data=validation_prediction_dataset,
        )

        base_file_name = f"{run_name}"
        model_file_path = os.path.join(cwd, f"{base_file_name}_model.txt")
        model_file_path = model.save(file_path=model_file_path)
        prediction_file_path = os.path.join(cwd, f"{base_file_name}_prediction.csv")
        prediction_file_path = validation_prediction.save(
            file_path=prediction_file_path
        )
        evaluation_file_path = os.path.join(cwd, f"{base_file_name}_evaluation.csv")
        evaluation_file_path = evaluation.save_data(file_path=evaluation_file_path)
        feature_importance_file_path = os.path.join(
            cwd, f"{base_file_name}_feature_importance.csv"
        )
        feature_importance_file_path = feature_importance.save(
            file_path=feature_importance_file_path
        )
        recommendation_file_path = os.path.join(
            cwd, f"{base_file_name}_recommendation.csv"
        )
        recommendation_file_path = validation_recommendation.save(
            file_path=recommendation_file_path
        )

        mlflow.log_artifact(model_file_path, "model")
        mlflow.log_artifact(prediction_file_path, "prediction")
        mlflow.log_artifact(evaluation_file_path, "evaluation")
        mlflow.log_artifact(feature_importance_file_path, "feature_importance")
        mlflow.log_artifact(recommendation_file_path, "recommendation")
        mlflow.log_metric(f"mean_absolute_error", evaluation.mean_absolute_error)
        mlflow.log_metric(
            f"root_mean_squared_error",
            evaluation.root_mean_squared_error,
        )

        logger.info(f"DONE machine learning task for {cfg.model.name}: {run_name}")

    logger.info("DONE machine_learning")


if __name__ == "__main__":
    main()
