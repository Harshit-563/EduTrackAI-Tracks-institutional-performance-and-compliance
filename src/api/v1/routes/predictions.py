from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from src.api.model_integration import ModelPredictor

router = APIRouter(tags=["Predictions"])
predictor = ModelPredictor()


def _normalize_institution_data(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "Student_Faculty_Ratio": payload.get("student_faculty_ratio", 0),
        "Faculty_Adequacy": payload.get("faculty_adequacy", 0),
        "Placement_Rate": payload.get("placement_rate", 0),
        "Infrastructure_Quality": payload.get("infrastructure_quality", 0),
        "Financial_Efficiency": payload.get("financial_efficiency", 0),
        "Fund_Utilization": payload.get("fund_utilization", 0),
        "Avg_Doc_DSS": payload.get("dss", payload.get("avg_doc_dss", 0)),
        "Missing_Doc_Count": payload.get("missing_doc_count", 0),
        "Total_Students": payload.get("total_students", 0),
        "Total_Faculty": payload.get("total_faculty", 0),
    }


def _build_response(raw_result: dict[str, Any], features: dict[str, Any]) -> dict[str, Any]:
    performance = raw_result.get("performance_tier", {}) or {}
    performance_prediction = {
        "tier": performance.get("performance_tier", "Unknown"),
        "confidence": float(performance.get("confidence", 0.0)),
        "probabilities": performance.get("probabilities", {}),
    }

    return {
        "risk_assessment": raw_result.get("risk_assessment", {}),
        "performance_prediction": performance_prediction,
        "anomaly_detection": raw_result.get("anomaly_detection", {}),
        "comprehensive_score": {
            "score": round(
                float(
                    (
                        features.get("Placement_Rate", 0)
                        + features.get("Infrastructure_Quality", 0)
                        + features.get("Financial_Efficiency", 0)
                        + features.get("Avg_Doc_DSS", 0)
                    )
                    / 4
                ),
                1,
            )
        },
    }


@router.post("/evaluate/institution")
def evaluate_institution(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        features = _normalize_institution_data(payload)
        raw_result = predictor.predict_all(features)
        return _build_response(raw_result, features)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Institution evaluation failed: {exc}") from exc
