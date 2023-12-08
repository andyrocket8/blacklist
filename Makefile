
_BUILD_ARGS_IMAGE_NAME ?= blacklist-app
_BUILD_ARGS_RELEASE_TAG ?= latest
_BUILD_ARGS_DOCKERFILE ?= ./src/Dockerfile

_builder:
		rm -f ./src/.mypy_cache
		docker build -t ${_BUILD_ARGS_IMAGE_NAME} -f ${_BUILD_ARGS_DOCKERFILE} .

_clean_builder:
		rm -f ./src/.mypy_cache
		docker build -t ${_BUILD_ARGS_IMAGE_NAME} --no-cache -f ${_BUILD_ARGS_DOCKERFILE} .

_test:
		docker run -i --rm --entrypoint sh ${_BUILD_ARGS_IMAGE_NAME} -c "flake8 -v --config setup.cfg"
		docker run -i --rm --entrypoint sh ${_BUILD_ARGS_IMAGE_NAME} -c "mypy src"
		docker run -i --rm --entrypoint sh ${_BUILD_ARGS_IMAGE_NAME} -c "pytest"

_start_redis:
		echo "set -a && source compose-redis.env && docker compose up -d" | bash

_stop_redis:
		echo "set -a && source compose-redis.env && docker compose down" | bash

_start_celery:
		echo "celery -A src.celery_app worker -l DEBUG" | bash

build:
		$(MAKE) _builder

test:
		$(MAKE) _test


clean_build:
		$(MAKE) _clean_builder

start_redis:
		$(MAKE) _start_redis

stop_redis:
		$(MAKE) _stop_redis


start_celery:
		$(MAKE) _start_celery &
