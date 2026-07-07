from __future__ import annotations

from typing import Any

from src.services.search_service import SemanticSearchService


class RAGService:
    def __init__(self, search_service: SemanticSearchService | None = None):
        self.search_service = search_service or SemanticSearchService()

    def answer_query(self, query: str, *, limit: int = 3) -> dict[str, Any]:
        documents = self.search_service.search(query, limit=limit)
        if not documents:
            return {
                "answer": "No relevant documents were found to support an answer.",
                "grounded": False,
                "citations": [],
            }

        context = "\n\n".join(
            f"Document {index + 1}: {item['excerpt']}"
            for index, item in enumerate(documents)
        )
        answer = self._build_answer(query, context)
        return {
            "answer": answer,
            "grounded": True,
            "citations": [
                {
                    "submission_code": item["submission_code"],
                    "doc_type": item["doc_type"],
                    "score": item["score"],
                }
                for item in documents
            ],
        }

    def _build_answer(self, query: str, context: str) -> str:
        return (
            f"Based on the retrieved documents, the best-supported answer to '{query}' is: "
            f"{context[:600]}"
        )
