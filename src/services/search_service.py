from __future__ import annotations

from pathlib import Path
from typing import Any

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

try:
    import chromadb
except Exception:
    chromadb = None

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None


class SemanticSearchService:
    _fallback_documents: list[dict[str, Any]] = []

    def __init__(self):
        self._client = None
        self._collection = None
        self._model = None

    def _get_collection(self):
        if self._collection is not None:
            return self._collection
        if chromadb is None:
            return None
        settings.chroma_persist_directory.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(settings.chroma_persist_directory))
        self._collection = self._client.get_or_create_collection(settings.vector_collection_name)
        return self._collection

    def _get_model(self):
        if self._model is not None:
            return self._model
        if SentenceTransformer is None:
            return None
        self._model = SentenceTransformer(settings.embedding_model_name)
        return self._model

    def index_document(self, *, document_id: str, text: str, metadata: dict[str, Any]) -> None:
        if not text:
            return

        self.__class__._fallback_documents = [
            item for item in self.__class__._fallback_documents if item["id"] != document_id
        ]
        self.__class__._fallback_documents.append({"id": document_id, "text": text, "metadata": metadata})

        collection = self._get_collection()
        model = self._get_model()
        if collection is None or model is None:
            logger.info("Semantic index skipped because vector backend dependencies are unavailable; using fallback index")
            return

        embedding = model.encode([text], convert_to_numpy=True)[0].tolist()
        collection.upsert(
            ids=[document_id],
            documents=[text[:8000]],
            metadatas=[metadata],
            embeddings=[embedding],
        )

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        collection = self._get_collection()
        model = self._get_model()
        if collection is None or model is None:
            query_lower = query.lower()
            matches = [
                {
                    "submission_code": item["id"],
                    "doc_type": item["metadata"].get("doc_type", "unknown"),
                    "score": 1.0 if query_lower in item["text"].lower() else 0.0,
                    "excerpt": item["text"][:240],
                    "metadata": item["metadata"],
                }
                for item in reversed(self.__class__._fallback_documents)
                if query_lower in item["text"].lower()
            ]
            return matches[:limit]

        embedding = model.encode([query], convert_to_numpy=True)[0].tolist()
        results = collection.query(query_embeddings=[embedding], n_results=limit)
        rows = []
        for index, doc_id in enumerate(results.get("ids", [[]])[0]):
            rows.append(
                {
                    "submission_code": doc_id,
                    "doc_type": results.get("metadatas", [[]])[0][index].get("doc_type", "unknown"),
                    "score": float(results.get("distances", [[]])[0][index] or 0.0),
                    "excerpt": (results.get("documents", [[]])[0][index] or "")[:240],
                    "metadata": results.get("metadatas", [[]])[0][index] or {},
                }
            )
        return rows
