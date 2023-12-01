
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


build:
		$(MAKE) _builder

test:
		$(MAKE) _test


clean_build:
		$(MAKE) _clean_builder