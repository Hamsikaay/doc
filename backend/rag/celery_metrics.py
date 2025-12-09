from prometheus_client import Counter, Histogram, start_http_server

# ✅ Count total tasks
CELERY_TASKS_TOTAL = Counter(
    "celery_tasks_total", "Total number of Celery tasks", ["task_name", "status"]
)

# ✅ Track task execution time
CELERY_TASK_LATENCY_SECONDS = Histogram(
    "celery_task_latency_seconds", "Celery task execution latency", ["task_name"]
)


# ✅ Start Prometheus metrics server
def start_metrics_server(port=9100):
    try:
        start_http_server(port)
        print(f"✅ Prometheus metrics server started on port {port}")
    except Exception as e:
        print("⚠️ Prometheus server already running:", e)
