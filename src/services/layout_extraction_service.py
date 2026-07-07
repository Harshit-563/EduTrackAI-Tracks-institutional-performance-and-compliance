from __future__ import annotations

import re
from typing import Any


class LayoutExtractionService:
    """Simple layout and table extraction service for document text."""

    def extract_layout_and_tables(self, text: str) -> dict[str, Any]:
        if not text:
            return {"layout_blocks": [], "tables": []}

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        blocks: list[str] = []
        table_rows: list[list[str]] = []
        current_table: list[str] = []

        for line in lines:
            if "|" in line:
                current_table.append(line)
                continue

            if current_table:
                table_rows.append(self._parse_table(current_table))
                current_table = []

            if self._looks_like_block(line):
                blocks.append(line)

        if current_table:
            table_rows.append(self._parse_table(current_table))

        return {
            "layout_blocks": blocks,
            "tables": [table for table in table_rows if table],
        }

    def _looks_like_block(self, line: str) -> bool:
        if not line:
            return False
        if re.fullmatch(r"[-|:]+", line):
            return False
        if line.startswith("http"):
            return False
        return True

    def _parse_table(self, rows: list[str]) -> list[dict[str, str]]:
        parsed: list[dict[str, str]] = []
        headers = [cell.strip() for cell in rows[0].split("|") if cell.strip()]
        for row in rows[1:]:
            if re.fullmatch(r"[-|:]+", row):
                continue
            cells = [cell.strip() for cell in row.split("|") if cell.strip()]
            if not cells:
                continue
            parsed.append(dict(zip(headers, cells)))
        return parsed
