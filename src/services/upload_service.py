from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path
import shutil
import uuid

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.core.config import settings
from src.database.models import DocumentStatus
from src.database.repositories import DocumentRepository
from src.services.audit_service import AuditService
from src.services.pipeline_service import DocumentProcessingDispatcher
from utils.logger import setup_logger


logger = setup_logger(__name__)


class UploadService:
    def __init__(self):
        self.storage_dir = settings.project_root / "data" / "uploads"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.audit_service = AuditService()
        self.dispatcher = DocumentProcessingDispatcher()

    def _validate_file_upload(self, file: UploadFile) -> None:
        if not file.filename:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Filename missing")

        file_ext = Path(file.filename).suffix.lower()
        allowed_uploads = {".pdf", ".png", ".jpg", ".jpeg", ".tiff"}
        if file_ext not in allowed_uploads:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(sorted(allowed_uploads))}",
            )

    async def upload_and_analyze(
        self,
        file: UploadFile,
        user: dict,
        db: Session,
        institution_id: int | None = None,
    ) -> dict:
        self._validate_file_upload(file)

        resolved_institution_id = institution_id or user.get("institution_id")
        if not resolved_institution_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Institution context is required")

        content = await file.read()
        if not content:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")
        max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
        if len(content) > max_size_bytes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file exceeds size limit")

        file_suffix = Path(file.filename).suffix.lower()
        document_code = f"SUB-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
        storage_path = self.storage_dir / f"{document_code}{file_suffix}"
        with open(storage_path, "wb") as handle:
            handle.write(content)

        content_hash = hashlib.sha256(content).hexdigest()

        repository = DocumentRepository(db)
        document = repository.create(
            submission_code=document_code,
            institution_id=resolved_institution_id,
            doc_type="pending_classification",
            original_filename=file.filename,
            storage_path=str(storage_path),
            mime_type=file.content_type,
            content_hash=content_hash,
            status=DocumentStatus.QUEUED,
            uploaded_by=user["user_id"],
            flags=[],
            extracted_fields={},
            metadata_json={"content_length": len(content)},
        )

        self.audit_service.log(
            db,
            action="document.uploaded",
            entity_type="document",
            entity_id=document.submission_code,
            user_id=user["user_id"],
            document_id=document.id,
            payload={"filename": file.filename, "mime_type": file.content_type},
        )
        db.commit()

        logger.info("Document upload initiated by %s: %s", user["email"], file.filename)
        return self.dispatcher.dispatch(document.id, db)
