from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.api.v1.schemas import ReviewActionPayload
from src.database.models import DocumentStatus
from src.database.repositories import DocumentRepository, ReviewActionRepository
from src.database.transaction import transactional
from src.services.audit_service import AuditService
from utils.logger import setup_logger


logger = setup_logger(__name__)
audit_service = AuditService()


class ReviewService:
    def get_reviewer_queue(self, user: dict, limit: int, offset: int, db: Session) -> dict:
        items = DocumentRepository(db).get_processing_queue(limit=limit, offset=offset)
        total = len(items)
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": [self._serialize_document(item) for item in items],
        }

    def get_submission(self, submission_id: str, user: dict, db: Session) -> dict:
        document = DocumentRepository(db).get_by_code(submission_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Submission {submission_id} not found")
        return self._serialize_document(document)

    def submit_review_action(self, submission_id: str, payload: ReviewActionPayload, user: dict, db: Session) -> dict:
        repository = DocumentRepository(db)
        document = repository.get_by_code(submission_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Submission {submission_id} not found")

        status_map = {
            "approved": DocumentStatus.APPROVED,
            "rejected": DocumentStatus.REJECTED,
            "needs_manual_review": DocumentStatus.NEEDS_MANUAL_REVIEW,
        }

        try:
            with transactional(db):
                repository.update_status(document, status_map[payload.action])
                ReviewActionRepository(db).create(
                    document_id=document.id,
                    reviewer_id=user["user_id"],
                    action=payload.action,
                    notes=payload.notes,
                )
                audit_service.log(
                    db,
                    action="document.reviewed",
                    entity_type="document",
                    entity_id=document.submission_code,
                    user_id=user["user_id"],
                    document_id=document.id,
                    payload={"action": payload.action, "notes": payload.notes},
                )
        except Exception:
            raise

        logger.info("Review submitted for %s by %s: %s", submission_id, user["email"], payload.action)
        return {
            "ok": True,
            "submission_id": submission_id,
            "status": payload.action,
            "reviewed_by": user["email"],
            "reviewed_at": datetime.utcnow().isoformat(),
        }

    def _serialize_document(self, document) -> dict:
        return {
            "id": document.submission_code,
            "institution": document.institution.name if document.institution else "Unknown",
            "institution_id": document.institution_id,
            "doc_type": document.doc_type,
            "dss": document.dss_score,
            "compliance_score": document.compliance_score,
            "status": document.status.value if hasattr(document.status, "value") else str(document.status),
            "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None,
            "flags": document.flags or [],
            "extracted_fields": document.extracted_fields or {},
            "classification_label": document.classification_label,
        }
