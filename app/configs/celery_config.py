from celery import Celery
from celery import signals
import os

from app.configs.log_config import setup_logger

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.celery_task"]
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    worker_concurrency=4  # Adjust based on CPU cores
)

@signals.worker_process_init.connect
def setup_logger_on_start(**kwargs):
    setup_logger()  # Re-initialize logger for each worker