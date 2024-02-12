# Multibuild to minimize image size
FROM python:3.11-alpine AS builder

WORKDIR /app
COPY poetry.lock pyproject.toml ./

# RUN apk --update add musl gcc build-base freetype-dev libpng-dev openblas-dev \
#  && apk add libpq-dev rust cargo curl \
#  && python -m pip install --no-cache-dir poetry==1.7.1 \
#  && poetry config virtualenvs.in-project true \
#  && poetry install --without dev --no-interaction --no-ansi --no-root \
#  && apk del gcc rust cargo postgresql build-base \
#  && rm -rf /var/cache/apk/*

RUN python -m pip install --no-cache-dir poetry==1.7.1 \
 && poetry config virtualenvs.in-project true \
 && poetry install --without dev,jupyter --no-interaction --no-ansi --no-root

# copy application files
COPY *.py /app/
COPY src /app/src


# Builder for development
FROM builder AS dev-builder
WORKDIR /app

# Add development dependencies
RUN poetry install --without jupyter --no-interaction --no-ansi --no-root
COPY setup.cfg /app/


# Image for development
FROM python:3.11-alpine AS dev-app
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app
COPY --from=dev-builder /app /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run development version of uvicorn based in main.py
CMD ["/app/.venv/bin/python", "./src/main.py"]

FROM python:3.11-alpine as base-app
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app

RUN apk --update add curl
COPY --from=builder /app /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["/app/.venv/bin/uvicorn", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "src.main:app"]

FROM python:3.11-alpine as celery-app
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
WORKDIR /app

COPY --from=builder /app /app
RUN apk --update add curl

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["/app/.venv/bin/celery", "-A", "src.celery_app", "worker", "-l", "DEBUG"]
