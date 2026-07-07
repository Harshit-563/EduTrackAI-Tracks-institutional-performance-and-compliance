from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from src.database.models import ReportType
from src.database.repositories import ReportRepository


class ReportService:
    def __init__(self):
        self.output_dir = Path("outputs/reports/document_pipeline")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_document_report(
        self,
        db: Session,
        *,
        document,
        payload: dict,
        summary: str,
    ):
        filename = f"{document.submission_code}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = self.output_dir / filename
        with open(file_path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, default=str)

        return ReportRepository(db).create(
            report_type=ReportType.DOCUMENT,
            document_id=document.id,
            institution_id=document.institution_id,
            title=f"Document report for {document.submission_code}",
            summary=summary,
            payload=payload,
            file_path=str(file_path),
        )
