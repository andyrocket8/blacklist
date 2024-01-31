
_BUILD_ARGS_IMAGE_NAME ?= blacklist-app
_BUILD_ARGS_RELEASE_TAG ?= latest
_BUILD_ARGS_DOCKERFILE ?= ./src/Dockerfile

_builder:
		docker build -t ${_BUILD_ARGS_IMAGE_NAME} -f ${_BUILD_ARGS_DOCKERFILE} . --target base-app

_clean_builder:
		rm -f ./src/.mypy_cache
		docker build -t ${_BUILD_ARGS_IMAGE_NAME} --no-cache -f ${_BUILD_ARGS_DOCKERFILE} . --target base-app

_test:
		docker run -i --rm --entrypoint sh ${_BUILD_ARGS_IMAGE_NAME} -c "source .venv/bin/activate && flake8 -v --config setup.cfg"
		docker run -i --rm --entrypoint sh ${_BUILD_ARGS_IMAGE_NAME} -c "source .venv/bin/activate && mypy ."
		docker run -i --rm --entrypoint sh ${_BUILD_ARGS_IMAGE_NAME} -c "source .venv/bin/activate && black ."
		docker run -i --rm --entrypoint sh ${_BUILD_ARGS_IMAGE_NAME} -c "source .venv/bin/activate && pytest"

_check:
		isort .
		flake8 -v --config setup.cfg
		mypy src
		black .
		pytest

_start_dev:
		echo "set -a && source compose-redis.env && docker compose -f docker-compose-dev.yml up -d" | bash

_stop_dev:
		echo "set -a && source compose-redis.env && docker compose -f docker-compose-dev.yml down" | bash

_start_local:
		echo "set -a && source compose-redis-local.env && docker compose --env-file compose-redis-local.env -f docker-compose.yml up -d --build" | bash

_stop_local:
		echo "set -a && source compose-redis-local.env && docker compose --env-file compose-redis-local.env -f docker-compose.yml down" | bash

_start_celery:
		echo "celery -A src.celery_app worker -l DEBUG" | bash

build:
		$(MAKE) _builder

check:
		$(MAKE) _check
test:
		$(MAKE) _test

clean_build:
		$(MAKE) _clean_builder

start_dev:
		# start development environment (redis)
		$(MAKE) _start_dev

stop_dev:
		# stop development environment (redis)
		$(MAKE) _stop_dev

start_local:
		# start development environment (redis)
		$(MAKE) _start_local

stop_local:
		# stop development environment (redis)
		$(MAKE) _stop_local

start_celery:
		$(MAKE) _start_celery &
