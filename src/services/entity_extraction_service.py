from __future__ import annotations

import re
from typing import Any


class EntityExtractionService:
    """Extract key/value pairs and entities from OCR text."""

    def extract_entities(self, text: str) -> dict[str, Any]:
        if not text:
            return {"entities": [], "key_value_pairs": {}}

        key_value_pairs: dict[str, str] = {}
        entities: list[dict[str, str]] = []

        for line in text.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if not key or not value:
                continue
            key_value_pairs[key] = value
            entities.append({"type": "key_value", "key": key, "value": value})

        return {
            "entities": entities,
            "key_value_pairs": key_value_pairs,
        }
