from __future__ import annotations

from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.compliance.scoring_engine import ComplianceScoringEngine
from src.database.repositories import DocumentRepository, InstitutionRepository
from src.services.audit_service import AuditService
from utils.logger import setup_logger


logger = setup_logger(__name__)
audit_service = AuditService()
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class InstitutionService:
    def get_submissions(self, institution_id: int, user: dict, limit: int, offset: int, db: Session) -> dict:
        self._authorize_access(institution_id, user)
        repository = DocumentRepository(db)
        documents = repository.get_by_institution(institution_id, limit, offset)
        return {
            "total": repository.count_by_institution(institution_id),
            "limit": limit,
            "offset": offset,
            "items": [self._serialize_document(item) for item in documents],
        }

    def get_overview(self, institution_id: int, user: dict, db: Session) -> dict:
        self._authorize_access(institution_id, user)
        institution = InstitutionRepository(db).get(institution_id)
        if not institution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

        submissions = DocumentRepository(db).get_by_institution(institution_id, limit=1000, offset=0)
        if not submissions:
            return {
                "institution_id": institution_id,
                "institution_name": institution.name,
                "avg_dss": 0,
                "compliance": 0,
                "pending_reviews": 0,
                "total_submissions": 0,
            }

        avg_dss = round(sum(float(item.dss_score or 0) for item in submissions) / len(submissions), 1)
        pending = sum(1 for item in submissions if str(item.status.value) in {"needs_manual_review", "low_confidence"})
        compliance = max(0, min(100, round(avg_dss - pending * 2, 1)))
        return {
            "institution_id": institution_id,
            "institution_name": institution.name,
            "avg_dss": avg_dss,
            "compliance": compliance,
            "pending_reviews": pending,
            "total_submissions": len(submissions),
        }

    def get_compliance_score(self, institution_id: int, user: dict, db: Session) -> dict:
        self._authorize_access(institution_id, user)
        institution = InstitutionRepository(db).get(institution_id)
        if not institution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found")

        submissions = DocumentRepository(db).get_by_institution(institution_id, limit=1000, offset=0)
        submission_dicts = [
            {
                "dss": item.dss_score,
                "status": item.status.value if hasattr(item.status, "value") else str(item.status),
                "doc_type": item.doc_type,
                "flags": item.flags or [],
            }
            for item in submissions
        ]
        metrics = {
            "total_students": institution.total_students,
            "total_faculty": institution.total_faculty,
            "placement_rate": institution.placement_rate,
            "fund_utilization": institution.fund_utilization,
            "infrastructure_area": institution.infrastructure_area,
        }
        result = ComplianceScoringEngine.calculate_compliance(submission_dicts, metrics)
        return {
            "institution_id": institution_id,
            "institution_name": institution.name,
            "overall_score": result.overall_score,
            "document_compliance": result.document_compliance,
            "risk_level": result.risk_level,
            "components": result.components,
            "recommendations": result.recommendations,
        }

    def get_dss_trend(self, institution_id: int, user: dict, db: Session) -> list[dict]:
        self._authorize_access(institution_id, user)
        documents = DocumentRepository(db).get_by_institution(institution_id, limit=1000, offset=0)
        trend = {}
        for document in documents:
            year = str((document.processed_at or document.created_at).year)
            trend.setdefault(year, []).append(float(document.dss_score or 0))
        return [
            {"year": year, "dss": round(sum(values) / len(values), 2)}
            for year, values in sorted(trend.items())
        ]

    def get_rank_list(self, user: dict, db: Session) -> dict:
        rows = self._build_institution_rank_list(db)
        return {
            "count": len(rows),
            "source": "computed_from_documents",
            "items": rows,
        }

    def _build_institution_rank_list(self, db: Session) -> list[dict]:
        document_repo = DocumentRepository(db)
        institution_repo = InstitutionRepository(db)
        all_documents = document_repo.list_all()
        all_institutions = institution_repo.list_all()

        grouped: dict[int, list] = {}
        for document in all_documents:
            grouped.setdefault(document.institution_id, []).append(document)

        rank_rows = []
        for institution in all_institutions:
            documents = grouped.get(institution.id, [])
            if not documents:
                continue
            dss_values = [float(item.dss_score or 0.0) for item in documents]
            avg_dss = round(sum(dss_values) / len(dss_values), 2) if dss_values else 0.0
            pending = sum(1 for item in documents if item.status.value in {"needs_manual_review", "low_confidence"})
            risk_score = max(0.0, min(100.0, (100.0 - avg_dss) + pending * 8.0))
            rank_score = round((avg_dss + (100 - risk_score)) / 2.0, 2)
            rank_rows.append(
                {
                    "institution": institution.name,
                    "avg_dss_score": avg_dss,
                    "risk_score": round(risk_score, 2),
                    "rank_score": rank_score,
                    "submission_count": len(documents),
                }
            )

        rank_rows.sort(key=lambda item: item["rank_score"], reverse=True)
        for index, row in enumerate(rank_rows, start=1):
            row["rank"] = index
        return rank_rows

    def _authorize_access(self, institution_id: int, user: dict) -> None:
        if user["role"] == "admin":
            return
        if user["institution_id"] != institution_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Institution access denied")

    def _serialize_document(self, document) -> dict:
        return {
            "id": document.submission_code,
            "institution": document.institution.name if document.institution else "Unknown",
            "institution_id": document.institution_id,
            "doc_type": document.doc_type,
            "dss": document.dss_score,
            "status": document.status.value if hasattr(document.status, "value") else str(document.status),
            "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None,
            "flags": document.flags or [],
            "extracted_fields": document.extracted_fields or {},
        }
