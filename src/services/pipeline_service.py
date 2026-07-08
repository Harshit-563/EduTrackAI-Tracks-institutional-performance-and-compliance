from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.api.model_integration import ModelPredictor
from src.compliance.scoring_engine import ComplianceScoringEngine
from src.database.models import DocumentStatus, PredictionType
from src.database.repositories import AIPredictionRepository, DocumentRepository, NotificationRepository
from src.services.audit_service import AuditService
from src.services.document_classification_service import DocumentClassificationService
from src.services.report_service import ReportService
from src.services.search_service import SemanticSearchService
from utils.logger import setup_logger

try:
    from doc_validator.compliance_engine import analyze_compliance_with_llm
except Exception:
    analyze_compliance_with_llm = None

try:
    from doc_validator.ocr_engine import run_ocr
    from doc_validator.predictor import predict_from_ocr
    OCR_AVAILABLE = True
except Exception:
    run_ocr = None
    predict_from_ocr = None
    OCR_AVAILABLE = False


logger = setup_logger(__name__)


class DocumentPipelineService:
    def __init__(self):
        self.classifier = DocumentClassificationService()
        self.predictor = ModelPredictor()
        self.report_service = ReportService()
        self.search_service = SemanticSearchService()
        self.audit_service = AuditService()

    def process_document(self, document_id: int, db: Session) -> dict[str, Any]:
        repository = DocumentRepository(db)
        document = repository.get_by_id(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if not document.storage_path:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document storage path missing")

        try:
            repository.update_status(document, DocumentStatus.PROCESSING)
            self.audit_service.log(
                db,
                action="document.processing_started",
                entity_type="document",
                entity_id=document.submission_code,
                user_id=document.uploaded_by,
                document_id=document.id,
            )
            db.flush()

            ocr_output = self._run_ocr(document.storage_path)
            full_text = ocr_output.get("full_text", "") or ""
            classification = self.classifier.classify(document.original_filename, full_text)
            ocr_output["doc_type"] = classification["label"]

            validation = self._run_validation(ocr_output)
            compliance_analysis = self._run_compliance(full_text, classification["label"], document.institution.name if document.institution else None)
            compliance_score = self._calculate_compliance(document, validation, compliance_analysis)
            predictions = self._run_predictions(document, validation, compliance_score)

            document.doc_type = classification["label"]
            document.classification_label = classification["label"]
            document.classification_confidence = classification["confidence"]
            document.ocr_text = full_text
            document.extracted_fields = validation.get("fields", {}) or {}
            document.dss_score = float(validation.get("dss_score", 0) or 0)
            document.compliance_score = compliance_score
            document.flags = sorted(
                {
                    *(validation.get("flags", []) or []),
                    *(compliance_analysis.get("flags", []) or []),
                }
            )
            document.metadata_json = {
                "ocr": {
                    "ocr_conf_mean": ocr_output.get("ocr_conf_mean"),
                    "page_count": ocr_output.get("page_count"),
                },
                "compliance_analysis": compliance_analysis,
            }
            document.processed_at = datetime.utcnow()
            document.status = self._resolve_status(document)

            self._persist_predictions(db, document, classification, validation, compliance_analysis, predictions, compliance_score)
            report_payload = {
                "document": {
                    "submission_code": document.submission_code,
                    "doc_type": document.doc_type,
                    "status": document.status.value,
                },
                "validation": validation,
                "compliance_analysis": compliance_analysis,
                "predictions": predictions,
            }
            self.report_service.create_document_report(
                db,
                document=document,
                payload=report_payload,
                summary=f"{document.doc_type} processed with status {document.status.value}",
            )
            NotificationRepository(db).create(
                user_id=document.uploaded_by,
                title="Document processed",
                message=f"{document.submission_code} completed with status {document.status.value}",
                metadata_json={"submission_code": document.submission_code},
            )
            self.search_service.index_document(
                document_id=document.submission_code,
                text=full_text,
                metadata={
                    "doc_type": document.doc_type,
                    "institution_id": document.institution_id,
                    "status": document.status.value,
                },
            )
            self.audit_service.log(
                db,
                action="document.processing_completed",
                entity_type="document",
                entity_id=document.submission_code,
                user_id=document.uploaded_by,
                document_id=document.id,
                payload={"status": document.status.value, "doc_type": document.doc_type},
            )
            db.commit()
        except Exception as exc:
            db.rollback()
            if document:
                document = repository.get_by_id(document_id)
                if document:
                    document.status = DocumentStatus.FAILED
                    document.flags = sorted({*(document.flags or []), f"pipeline_error:{exc}"})
                    document.processed_at = datetime.utcnow()
                    self.audit_service.log(
                        db,
                        action="document.processing_failed",
                        entity_type="document",
                        entity_id=document.submission_code,
                        user_id=document.uploaded_by,
                        document_id=document.id,
                        payload={"error": str(exc)},
                    )
                    db.commit()
            raise

        return {
            "submission_id": document.submission_code,
            "file_name": document.original_filename,
            "dss": document.dss_score,
            "compliance_score": document.compliance_score,
            "status": document.status.value,
            "compliance": "Compliant" if (document.compliance_score or 0) >= 75 else "Needs Correction",
            "fields": document.extracted_fields,
            "flags": document.flags,
            "classification": {
                "label": document.classification_label,
                "confidence": document.classification_confidence,
            },
        }

    def _run_ocr(self, file_path: str) -> dict[str, Any]:
        if not OCR_AVAILABLE or run_ocr is None:
            raise RuntimeError("OCR pipeline unavailable")
        return run_ocr(file_path)

    def _run_validation(self, ocr_output: dict[str, Any]) -> dict[str, Any]:
        if predict_from_ocr is None:
            return {
                "dss_score": 0,
                "flags": ["validator_unavailable"],
                "fields": {},
            }
        return predict_from_ocr(ocr_output)

    def _run_compliance(self, full_text: str, doc_type: str, institution_name: str | None) -> dict[str, Any]:
        if analyze_compliance_with_llm is None:
            return {
                "success": False,
                "compliance_status": "Undetermined",
                "flags": ["llm_compliance_unavailable"],
            }
        return analyze_compliance_with_llm(full_text, doc_type, institution_name)

    def _calculate_compliance(self, document, validation: dict[str, Any], compliance_analysis: dict[str, Any]) -> float:
        metrics = {
            "total_students": document.institution.total_students if document.institution else 0,
            "total_faculty": document.institution.total_faculty if document.institution else 0,
            "placement_rate": document.institution.placement_rate if document.institution else 0,
            "fund_utilization": document.institution.fund_utilization if document.institution else 0,
            "infrastructure_area": document.institution.infrastructure_area if document.institution else 0,
        }
        result = ComplianceScoringEngine.calculate_compliance(
            [
                {
                    "dss": validation.get("dss_score", 0),
                    "status": validation.get("status", "needs_manual_review"),
                    "doc_type": document.doc_type,
                    "flags": validation.get("flags", []),
                }
            ],
            metrics,
        )
        llm_bonus = 10 if compliance_analysis.get("compliance_status") == "Compliant" else 0
        llm_penalty = 10 if compliance_analysis.get("compliance_status") == "Non-Compliant" else 0
        return round(max(0, min(100, result.overall_score + llm_bonus - llm_penalty)), 2)

    def _run_predictions(self, document, validation: dict[str, Any], compliance_score: float) -> dict[str, Any]:
        features = {
            "Student_Faculty_Ratio": (
                (document.institution.total_students or 0) / max(document.institution.total_faculty or 1, 1)
                if document.institution
                else 0
            ),
            "Faculty_Adequacy": 100,
            "Placement_Rate": document.institution.placement_rate if document.institution else 0,
            "Infrastructure_Quality": min(100, float(document.institution.infrastructure_area or 0) / 100) if document.institution else 0,
            "Financial_Efficiency": document.institution.fund_utilization if document.institution else 0,
            "Fund_Utilization": document.institution.fund_utilization if document.institution else 0,
            "Avg_Doc_DSS": float(validation.get("dss_score", 0) or 0),
            "Missing_Doc_Count": 0 if compliance_score >= 70 else 1,
            "Total_Students": document.institution.total_students if document.institution else 0,
            "Total_Faculty": document.institution.total_faculty if document.institution else 0,
        }
        return self.predictor.predict_all(features)

    def _persist_predictions(
        self,
        db: Session,
        document,
        classification: dict[str, Any],
        validation: dict[str, Any],
        compliance_analysis: dict[str, Any],
        predictions: dict[str, Any],
        compliance_score: float,
    ) -> None:
        repository = AIPredictionRepository(db)
        repository.create(
            document_id=document.id,
            prediction_type=PredictionType.CLASSIFICATION,
            model_name="keyword_classifier",
            score=classification["confidence"],
            label=classification["label"],
            confidence=classification["confidence"],
            explanation={"method": "keyword_coverage"},
            payload=classification,
        )
        repository.create(
            document_id=document.id,
            prediction_type=PredictionType.COMPLIANCE,
            model_name=compliance_analysis.get("llm_model", "hybrid_compliance"),
            score=compliance_score,
            label=compliance_analysis.get("compliance_status", "Undetermined"),
            confidence=validation.get("ocr_confidence"),
            explanation={"flags": compliance_analysis.get("flags", []), "validation_flags": validation.get("flags", [])},
            payload=compliance_analysis,
        )

        mapping = {
            PredictionType.RISK: predictions.get("risk_assessment", {}),
            PredictionType.PERFORMANCE: predictions.get("performance_tier", {}),
            PredictionType.ANOMALY: predictions.get("anomaly_detection", {}),
        }
        for prediction_type, payload in mapping.items():
            repository.create(
                document_id=document.id,
                prediction_type=prediction_type,
                model_name="model_predictor",
                score=payload.get("risk_probability") or payload.get("anomaly_score") or payload.get("confidence"),
                label=payload.get("risk_level") or payload.get("performance_tier") or payload.get("status"),
                confidence=payload.get("confidence"),
                explanation={"payload_keys": sorted(payload.keys())},
                payload=payload,
            )

    def _resolve_status(self, document) -> DocumentStatus:
        if any(flag.startswith("pipeline_error") for flag in document.flags or []):
            return DocumentStatus.FAILED
        if (document.compliance_score or 0) >= 75 and (document.dss_score or 0) >= 75:
            return DocumentStatus.PARSED
        if (document.dss_score or 0) < 55:
            return DocumentStatus.LOW_CONFIDENCE
        return DocumentStatus.NEEDS_MANUAL_REVIEW


class DocumentProcessingDispatcher:
    def dispatch(self, document_id: int, db: Session) -> dict[str, Any]:
        from src.core.config import settings
        from src.workers.tasks import process_document_task

        if settings.worker_enabled and process_document_task is not None:
            process_document_task.delay(document_id)
            return {"queued": True, "document_id": document_id}
        return DocumentPipelineService().process_document(document_id, db)


__all__ = ["DocumentPipelineService", "DocumentProcessingDispatcher", "OCR_AVAILABLE"]
