import os

import mlflow  # type: ignore
from omegaconf import DictConfig

import hydra
from src.domain.prediction_data import PredictionDataset
from src.domain.training_data import TrainingDataset
from src.infrastructure.database import PostgreSQLClient
from src.middleware.logger import configure_logger
from src.ml_algos.lightgbm_regressor import LightGBMRegression
from src.ml_algos.models import get_model
from src.ml_algos.preprocess import GenreExtractor, RatingExtractor
from src.repository.movies_repository import MoviesRepository
from src.repository.ratings_repository import RatingsRepository
from src.repository.tags_repository import TagsRepository
from src.usecase.data_loader_usecase import DataLoaderUsecase
from src.usecase.evaluation_usecase import EvaluationUsecase
from src.usecase.prediction_usecase import PredictionUsecase
from src.usecase.preprocess_usecase import PreprocessUsecase
from src.usecase.training_usecase import TrainingUsecase

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

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"))
    mlflow.set_experiment(cfg.name)
    with mlflow.start_run(run_name=run_name):

        mlflow.log_artifact(os.path.join(cwd, ".hydra/config.yaml"))
        mlflow.log_artifact(os.path.join(cwd, ".hydra/hydra.yaml"))
        mlflow.log_artifact(os.path.join(cwd, ".hydra/overrides.yaml"))

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

        rating_extractor = RatingExtractor()
        genre_extractor = GenreExtractor()

        preprocess_usecase = PreprocessUsecase(
            rating_extractor=rating_extractor,
            genre_extractor=genre_extractor,
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

        training_dataset = TrainingDataset(
            training_data=preprocessed_dataset.training_data,
            validation_data=preprocessed_dataset.validation_data,
        )

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
            user_id=validation_prediction.prediction.user_id.tolist(),
            recency_id=validation_prediction.prediction.recency_id.tolist(),
            movie_id=validation_prediction.prediction.movie_id.tolist(),
            y_true=preprocessed_dataset.validation_data.y.rating.tolist(),
            y_pred=validation_prediction.prediction.prediction.tolist(),
        )

        feature_importance = evaluation_usecase.export_feature_importance(model=model)

        base_file_name = f"{run_name}"
        model_file_path = os.path.join(cwd, f"{base_file_name}_model.txt")
        model_file_path = model.save(file_path=model_file_path)
        evaluation_file_path = os.path.join(cwd, f"{base_file_name}_evaluation.csv")
        evaluation_file_path = evaluation.save_data(file_path=evaluation_file_path)
        feature_importance_file_path = os.path.join(
            cwd, f"{base_file_name}_feature_importance.csv"
        )
        feature_importance_file_path = feature_importance.save(
            file_path=feature_importance_file_path
        )

        mlflow.log_artifact(model_file_path, "model")
        mlflow.log_artifact(evaluation_file_path, "evaluation")
        mlflow.log_artifact(feature_importance_file_path, "feature_importance")
        mlflow.log_metric(f"mean_absolute_error", evaluation.mean_absolute_error)
        mlflow.log_metric(
            f"root_mean_squared_error",
            evaluation.root_mean_squared_error,
        )

        logger.info(f"DONE machine learning task for {cfg.model.name}: {run_name}")

    logger.info("DONE machine_learning")


if __name__ == "__main__":
    main()
