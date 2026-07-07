from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.v1.schemas import DocumentSearchResponse
from src.auth.dependencies import get_current_user, get_optional_current_user
from src.services.rag_service import RAGService
from src.services.search_service import SemanticSearchService


router = APIRouter(tags=["Documents"])
search_service = SemanticSearchService()
rag_service = RAGService(search_service)


@router.get("/documents/search", response_model=list[DocumentSearchResponse])
def semantic_search(
    q: str = Query(..., min_length=3),
    limit: int = Query(5, ge=1, le=20),
    user=Depends(get_current_user),
):
    return search_service.search(q, limit=limit)


@router.post("/documents/ask")
def ask_documents(payload: dict, user=Depends(get_optional_current_user)):
    try:
        query = payload.get("query", "")
        limit = int(payload.get("limit", 3) or 3)
        if not query.strip():
            raise HTTPException(status_code=400, detail="Query is required")
        return rag_service.answer_query(query, limit=limit)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive path
        raise HTTPException(status_code=500, detail=f"RAG request failed: {exc}") from exc
