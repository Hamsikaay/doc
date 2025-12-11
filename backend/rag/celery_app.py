from celery import Celery
import os
from logging_config import configure_logging 


configure_logging()  

BROKER = os.getenv("CELERY_BROKER_URL", "amqp://user:pass@localhost:5672//")
BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery = Celery(
    "rag",
    broker=BROKER,
    backend=BACKEND,
)

# IMPORTANT: explicitly import tasks so workers register them
celery.autodiscover_tasks(['rag'])

