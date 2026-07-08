from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from src.api.v1.schemas import DocumentSearchResponse
from src.auth.dependencies import get_current_user
from src.services.search_service import SemanticSearchService


router = APIRouter(tags=["Documents"])
search_service = SemanticSearchService()


@router.get("/documents/search", response_model=list[DocumentSearchResponse])
def semantic_search(
    q: str = Query(..., min_length=3),
    limit: int = Query(5, ge=1, le=20),
    user=Depends(get_current_user),
):
    return search_service.search(q, limit=limit)
