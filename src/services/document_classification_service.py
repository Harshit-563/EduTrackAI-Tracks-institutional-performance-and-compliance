from __future__ import annotations

from pathlib import Path

try:
    from doc_validator.predictor import REQUIRED_KEYWORDS
except Exception:
    REQUIRED_KEYWORDS = {}


class DocumentClassificationService:
    def classify(self, filename: str | None, text: str) -> dict:
        text_lower = (text or "").lower()
        filename_lower = (filename or "").lower()

        best_label = "general_document"
        best_score = 0.0

        for label, keywords in REQUIRED_KEYWORDS.items():
            if not keywords:
                continue
            keyword_matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
            score = keyword_matches / len(keywords)
            if label.replace("_", " ") in filename_lower:
                score = max(score, 0.8)
            if score > best_score:
                best_label = label
                best_score = score

        if best_score == 0.0:
            suffix = Path(filename or "").suffix.lower()
            if suffix == ".pdf":
                best_score = 0.35
            else:
                best_score = 0.25

        return {
            "label": best_label,
            "confidence": round(best_score, 3),
        }
