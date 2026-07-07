from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.api.v1.schemas import ReviewActionPayload
from src.auth.dependencies import require_roles
from src.core.exceptions import ServerError, ValidationError
from src.database import get_db
from src.database.models import UserRole
from src.services.review_service import ReviewService


router = APIRouter(tags=["Reviewer"])
review_service = ReviewService()
reviewer_user = require_roles(UserRole.REVIEWER, UserRole.ADMIN)


@router.get("/reviewer/queue")
def reviewer_queue(
    user=Depends(reviewer_user),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    try:
        return review_service.get_reviewer_queue(user, limit, offset, db)
    except (HTTPException, ValidationError, ServerError):
        raise
    except Exception as exc:
        raise ServerError(detail=f"Failed to retrieve queue: {exc}") from exc


@router.get("/reviewer/document/{submission_id}")
def reviewer_document(
    submission_id: str,
    user=Depends(reviewer_user),
    db: Session = Depends(get_db),
):
    try:
        return review_service.get_submission(submission_id, user, db)
    except (HTTPException, ValidationError, ServerError):
        raise
    except Exception as exc:
        raise ServerError(detail=f"Failed to retrieve document: {exc}") from exc


@router.post("/reviews/{submission_id}/action")
def review_action(
    submission_id: str,
    payload: ReviewActionPayload,
    user=Depends(reviewer_user),
    db: Session = Depends(get_db),
):
    try:
        return review_service.submit_review_action(submission_id, payload, user, db)
    except (HTTPException, ValidationError, ServerError):
        raise
    except Exception as exc:
        raise ServerError(detail=f"Failed to submit review: {exc}") from exc
