from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.auth.dependencies import require_roles
from src.database import get_db
from src.database.models import UserRole
from src.services.institution_service import InstitutionService


router = APIRouter(tags=["Institutions"])
institution_service = InstitutionService()
institution_user = require_roles(UserRole.INSTITUTION, UserRole.ADMIN)


@router.get("/institutions/{institution_id}/submissions")
def institution_submissions(
    institution_id: int,
    user=Depends(institution_user),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        return institution_service.get_submissions(institution_id, user, limit, offset, db)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve submissions: {exc}")


@router.get("/institutions/{institution_id}/overview")
def institution_overview(
    institution_id: int,
    user=Depends(institution_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        return institution_service.get_overview(institution_id, user, db)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve overview: {exc}")


@router.get("/institutions/{institution_id}/compliance")
def institution_compliance(
    institution_id: int,
    user=Depends(institution_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        return institution_service.get_compliance_score(institution_id, user, db)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve compliance score: {exc}")


@router.get("/institutions/{institution_id}/dss-trend")
def institution_dss_trend(
    institution_id: int,
    user=Depends(institution_user),
    db: Session = Depends(get_db),
) -> Any:
    try:
        return institution_service.get_dss_trend(institution_id, user, db)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trend: {exc}")


@router.get("/institutions/rank-list")
def institution_rank_list(
    user=Depends(institution_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        return institution_service.get_rank_list(user, db)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve rank list: {exc}")
