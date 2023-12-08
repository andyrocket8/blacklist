from celery import Celery  # type: ignore[import-untyped]

from src.core.config import app_settings

redis_connection_str = app_settings.get_redis_uri_for_celery()

# define celery application
app = Celery(
    'src',
    broker=redis_connection_str,
    include=['src.tasks.celery_tasks'],
)

app.conf.update(
    result_expires=3600,
)
