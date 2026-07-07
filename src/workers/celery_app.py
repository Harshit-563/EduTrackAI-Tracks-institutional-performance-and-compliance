from __future__ import annotations

from src.core.config import settings

try:
    from celery import Celery
except Exception:
    Celery = None


def get_celery_app():
    if Celery is None or not settings.celery_broker_url:
        return None

    app = Celery(
        "edutrack",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend or settings.celery_broker_url,
    )
    app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"])
    return app


celery_app = get_celery_app()
