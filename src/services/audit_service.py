from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from src.database.repositories import AuditLogRepository


class AuditService:
    def log(
        self,
        db: Session,
        *,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: int | None = None,
        document_id: int | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        AuditLogRepository(db).create(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            document_id=document_id,
            payload=payload or {},
        )
