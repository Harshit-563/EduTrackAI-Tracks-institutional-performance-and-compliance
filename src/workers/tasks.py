from __future__ import annotations

from src.database import session_scope
from src.services.pipeline_service import DocumentPipelineService
from src.workers.celery_app import celery_app


process_document_task = None


if celery_app is not None:

    @celery_app.task(name="edutrack.process_document")
    def process_document_task(document_id: int):
        with session_scope() as db:
            return DocumentPipelineService().process_document(document_id, db)
