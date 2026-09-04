from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "axontime_workers",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=True,
    task_eager_propagates=True,
    broker_connection_retry_on_startup=False,
    broker_connection_max_retries=1,
    task_publish_retry=False,
)

@celery_app.task(name="ping_task")
def ping_task() -> str:
    return "pong"
