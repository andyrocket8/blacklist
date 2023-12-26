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
 && poetry install --without dev --no-interaction --no-ansi --no-root


FROM python:3.11-alpine as base-app

WORKDIR /app

COPY --from=builder /app /app
COPY src /app/src
COPY manage.py /app/
COPY setup.cfg /app/

RUN apk --update add curl

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["/app/.venv/bin/uvicorn", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "src.main:app"]

FROM python:3.11-alpine as celery-app

WORKDIR /app

COPY --from=builder /app /app
COPY src /app/src

RUN apk --update add curl

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["/app/.venv/bin/celery", "-A", "src.celery_app", "worker", "-l", "DEBUG"]
