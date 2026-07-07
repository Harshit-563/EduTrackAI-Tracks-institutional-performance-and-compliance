from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.auth.dependencies import require_roles
from src.core.exceptions import ServerError, ValidationError
from src.database import get_db
from src.database.models import UserRole
from src.services.upload_service import UploadService


router = APIRouter(tags=["Upload"])
upload_service = UploadService()
uploader_user = require_roles(UserRole.INSTITUTION, UserRole.ADMIN)


@router.post("/upload-analyze")
async def upload_analyze(
    file: UploadFile = File(...),
    institution_id: int | None = Form(default=None),
    user=Depends(uploader_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        return await upload_service.upload_and_analyze(file, user, db, institution_id=institution_id)
    except (HTTPException, ValidationError, ServerError):
        raise
    except Exception as exc:
        raise ServerError(detail=f"Upload analyze failed: {exc}") from exc
