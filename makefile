ABSOLUTE_PATH := $(shell pwd)
DOCKERFILE := Dockerfile
DOCKER_COMPOSE := docker-compose.yaml
VERSION := 1.0.0

DOCKER_REPOSITORY := recommend_movielens

DIR := $(ABSOLUTE_PATH)
TAG = recommend_movielens
PLATFORM := linux/amd64


############ RECOMMEND_MOVIELENS DATA_REGISTRATION COMMANDS ############
DATA_REGISTRATION_DIR := $(DIR)/data_registration
DOCKERFILE_DATA_REGISTRATION = $(DATA_REGISTRATION_DIR)/$(DOCKERFILE)
DOCKER_DATA_REGISTRATION_TAG = $(TAG)_data_registration
DOCKER_DATA_REGISTRATION_IMAGE_NAME = $(DOCKER_REPOSITORY):$(DOCKER_DATA_REGISTRATION_TAG)_$(VERSION)

.PHONY: req_data_registration
req_data_registration:
	cd $(DATA_REGISTRATION_DIR) && \
	poetry export \
		--without-hashes \
		-f requirements.txt \
		--output requirements.txt

.PHONY: build_data_registration
build_data_registration:
	docker build \
		--platform $(PLATFORM) \
		-t $(DOCKER_DATA_REGISTRATION_IMAGE_NAME) \
		-f $(DOCKERFILE_DATA_REGISTRATION) \
		.


############ RECOMMEND_MOVIELENS MLFLOW COMMANDS ############
MLFLOW_DIR := $(DIR)/mlflow
DOCKERFILE_MLFLOW = $(MLFLOW_DIR)/$(DOCKERFILE)
DOCKER_MLFLOW_TAG = $(TAG)_mlflow
DOCKER_MLFLOW_IMAGE_NAME = $(DOCKER_REPOSITORY):$(DOCKER_MLFLOW_TAG)_$(VERSION)

.PHONY: req_mlflow
req_mlflow:
	cd $(MLFLOW_DIR) && \
	poetry export \
		--without-hashes \
		-f requirements.txt \
		--output requirements.txt

.PHONY: build_mlflow
build_mlflow:
	docker build \
		--platform $(PLATFORM) \
		-t $(DOCKER_MLFLOW_IMAGE_NAME) \
		-f $(DOCKERFILE_MLFLOW) \
		.


############ RECOMMEND_MOVIELENS MACHINE_LEARNING COMMANDS ############
MACHINE_LEARNING_DIR := $(DIR)/machine_learning
DOCKERFILE_MACHINE_LEARNING = $(MACHINE_LEARNING_DIR)/$(DOCKERFILE)
DOCKER_MACHINE_LEARNING_TAG = $(TAG)_machine_learning
DOCKER_MACHINE_LEARNING_IMAGE_NAME = $(DOCKER_REPOSITORY):$(DOCKER_MACHINE_LEARNING_TAG)_$(VERSION)

.PHONY: req_machine_learning
req_machine_learning:
	cd $(MACHINE_LEARNING_DIR) && \
	poetry export \
		--without-hashes \
		-f requirements.txt \
		--output requirements.txt

.PHONY: build_machine_learning
build_machine_learning:
	docker build \
		--platform $(PLATFORM) \
		-t $(DOCKER_MACHINE_LEARNING_IMAGE_NAME) \
		-f $(DOCKERFILE_MACHINE_LEARNING) \
		.

.PHONY: run_machine_learning
run_machine_learning:
	docker run \
		-it \
		--name machine_learning \
		-e POSTGRES_HOST=postgres \
		-e POSTGRES_PORT=5432 \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_PASSWORD=password \
		-e POSTGRES_DBNAME=recommend_movielens \
		-e MLFLOW_TRACKING_URI=http://mlflow:5000 \
		-e TARGET_CONFIG=default \
		-v $(MACHINE_LEARNING_DIR)/hydra:/opt/hydra \
		-v $(MACHINE_LEARNING_DIR)/src:/opt/src \
		-v $(MACHINE_LEARNING_DIR)/outputs:/opt/outputs \
		--net recommend_movielens \
		$(DOCKER_MACHINE_LEARNING_IMAGE_NAME) \
		python -m src.main


############ RECOMMEND_MOVIELENS NOTEBOOK COMMANDS ############
NOTEBOOK_DIR := $(DIR)/notebook
DOCKERFILE_NOTEBOOK = $(NOTEBOOK_DIR)/$(DOCKERFILE)
DOCKER_NOTEBOOK_TAG = $(TAG)_notebook
DOCKER_NOTEBOOK_IMAGE_NAME = $(DOCKER_REPOSITORY):$(DOCKER_NOTEBOOK_TAG)_$(VERSION)

.PHONY: req_notebook
req_notebook:
	cd $(NOTEBOOK_DIR) && \
	poetry export \
		--without-hashes \
		-f requirements.txt \
		--output requirements.txt

.PHONY: build_notebook
build_notebook:
	docker build \
		--platform $(PLATFORM) \
		-t $(DOCKER_NOTEBOOK_IMAGE_NAME) \
		-f $(DOCKERFILE_NOTEBOOK) \
		.

.PHONY: run_notebook
run_notebook:
	docker run \
		-it \
		--rm \
		--name notebook \
		-v $(DIR):/opt \
		-p 8888:8888 \
		$(DOCKER_NOTEBOOK_IMAGE_NAME) \
		jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.token=''


############ ALL COMMANDS ############
.PHONY: req_all
req_all: req_data_registration \
	req_machine_learning \
	req_mlflow \
	req_notebook \

.PHONY: build_all
build_all: build_data_registration \
	build_machine_learning \
	build_mlflow \
	build_notebook \


############ DOCKER COMPOSE COMMANDS ############
.PHONY: up
up:
	docker compose \
		-f $(DOCKER_COMPOSE) \
		up -d

.PHONY: down
down:
	docker compose \
		-f $(DOCKER_COMPOSE) \
		down
