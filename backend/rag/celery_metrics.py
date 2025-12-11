from prometheus_client import Counter, Histogram, start_http_server

from celery.signals import worker_process_init
from prometheus_client import start_http_server
# ✅ Count total tasks
CELERY_TASKS_TOTAL = Counter(
    "celery_tasks_total", "Total number of Celery tasks", ["task_name", "status"]
)

# ✅ Track task execution time
CELERY_TASK_LATENCY_SECONDS = Histogram(
    "celery_task_latency_seconds", "Celery task execution latency", ["task_name"]
)


@worker_process_init.connect
def start_prometheus_in_worker(**kwargs):
    start_http_server(9100)
