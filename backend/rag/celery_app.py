# # celery_app.py
# """
# Create a Celery app instance. We use environment variables if available so
# the same code can run locally (localhost) or inside Docker Compose (service names).
# """
# import os
# from celery import Celery

# BROKER = os.getenv("CELERY_BROKER_URL", "amqp://user:pass@localhost:5672//")
# BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# celery = Celery("rag_demo", broker=BROKER, backend=BACKEND)

# # optional: make sure workers send 'started' events
# # celery.conf.task_track_started = True
# import rag.tasks

# # optional serializers config (pickle is default and supports bytes)
# # celery.conf.update(task_serializer='pickle', accept_content=['pickle', 'json', 'application/x-python-serialize'])
from celery import Celery
import os

BROKER = os.getenv("CELERY_BROKER_URL", "amqp://user:pass@localhost:5672//")
BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery = Celery(
    "rag",
    broker=BROKER,
    backend=BACKEND,
)

# IMPORTANT: explicitly import tasks so workers register them
celery.autodiscover_tasks(['rag'])

