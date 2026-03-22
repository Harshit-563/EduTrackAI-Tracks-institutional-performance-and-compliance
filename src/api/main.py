"""
EduTrack FastAPI Backend with ML Model Integration
- REST API endpoints for institutional evaluation
- Real-time ML predictions
- Document processing pipeline
- Authentication and authorization
"""

from fastapi import FastAPI, HTTPException, Depends, Query, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import pandas as pd
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

from .model_integration import ModelPredictor, InstitutionScorer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EduTrack API",
    description="Institutional Evaluation and Risk Assessment API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML predictor
try:
    predictor = ModelPredictor()
    scorer = InstitutionScorer(predictor)
    ML_AVAILABLE = True
    logger.info("ML models loaded successfully")
except Exception as e:
    ML_AVAILABLE = False
    logger.error(f"Could not load ML models: {str(e)}")


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class InstitutionBase(BaseModel):
    """Base institution model"""
    college_name: str = Field(..., min_length=1)
    state: str
    city: str
    college_type: str


class InstitutionMetrics(InstitutionBase):
    """Institution with full metrics"""
    total_students: float
    total_faculty: float
    placement_rate: float = Field(..., ge=0, le=100)
    fund_utilization: float = Field(..., ge=0, le=100)
    avg_doc_dss: float = Field(..., ge=0, le=100)
    student_faculty_ratio: float = Field(..., gt=0)
    faculty_adequacy: float = Field(..., ge=0, le=100)
    infrastructure_quality: float = Field(..., ge=0, le=100)
    financial_efficiency: float = Field(..., ge=0, le=100)
    missing_doc_count: int = Field(..., ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "college_name": "IIT Delhi",
                "state": "Delhi",
                "city": "Delhi",
                "college_type": "Public",
                "total_students": 5000,
                "total_faculty": 200,
                "placement_rate": 95.0,
                "fund_utilization": 85.0,
                "avg_doc_dss": 95.0,
                "student_faculty_ratio": 25.0,
                "faculty_adequacy": 90.0,
                "infrastructure_quality": 85.0,
                "financial_efficiency": 85.0,
                "missing_doc_count": 0
            }
        }


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response"""
    college_name: str
    risk_level: str
    risk_probability: float
    confidence: float
    details: Dict[str, Any]


class PerformanceTierResponse(BaseModel):
    """Performance tier response"""
    college_name: str
    performance_tier: str
    confidence: float
    overall_score: float


class AnomalyDetectionResponse(BaseModel):
    """Anomaly detection response"""
    college_name: str
    is_anomalous: bool
    anomaly_score: float
    status: str


class ComprehensiveScoreResponse(BaseModel):
    """Comprehensive scoring response"""
    college_name: str
    overall_score: float
    metrics: Dict[str, float]
    risk_assessment: Dict[str, Any]
    performance_tier: Dict[str, Any]
    anomaly_detection: Dict[str, Any]
    timestamp: str


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    ml_models_available: bool
    models: List[str] = []


# ============================================================================
# HEALTH & DIAGNOSTICS
# ============================================================================

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns:
        HealthCheckResponse with system status
    """
    models_available = []
    if ML_AVAILABLE:
        models_available = ['risk_assessment', 'performance_tier', 'anomaly_detection']
    
    return HealthCheckResponse(
        status="healthy" if ML_AVAILABLE else "degraded",
        timestamp=datetime.now().isoformat(),
        ml_models_available=ML_AVAILABLE,
        models=models_available
    )


# ============================================================================
# PREDICTIONS & SCORING
# ============================================================================

@app.post("/predict/risk", response_model=RiskAssessmentResponse, tags=["Predictions"])
async def predict_risk(metrics: InstitutionMetrics):
    """
    Predict institutional risk level
    
    Args:
        metrics: Institution metrics
        
    Returns:
        RiskAssessmentResponse with risk prediction
    """
    if not ML_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML models not available")
    
    try:
        features = {
            'Student_Faculty_Ratio': metrics.student_faculty_ratio,
            'Faculty_Adequacy': metrics.faculty_adequacy,
            'Placement_Rate': metrics.placement_rate,
            'Infrastructure_Quality': metrics.infrastructure_quality,
            'Financial_Efficiency': metrics.financial_efficiency,
            'Fund_Utilization': metrics.fund_utilization,
            'Avg_Doc_DSS': metrics.avg_doc_dss,
            'Missing_Doc_Count': metrics.missing_doc_count,
            'Total_Students': metrics.total_students,
            'Total_Faculty': metrics.total_faculty
        }
        
        prediction = predictor.predict_risk_level(features)
        
        if 'error' in prediction:
            raise HTTPException(status_code=400, detail=prediction['error'])
        
        return RiskAssessmentResponse(
            college_name=metrics.college_name,
            risk_level=prediction['risk_level'],
            risk_probability=prediction['risk_probability'],
            confidence=prediction['confidence'],
            details=prediction
        )
    except Exception as e:
        logger.error(f"Risk prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/performance", response_model=PerformanceTierResponse, tags=["Predictions"])
async def predict_performance(metrics: InstitutionMetrics):
    """
    Predict institutional performance tier
    
    Args:
        metrics: Institution metrics
        
    Returns:
        PerformanceTierResponse with performance prediction
    """
    if not ML_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML models not available")
    
    try:
        features = {
            'Student_Faculty_Ratio': metrics.student_faculty_ratio,
            'Faculty_Adequacy': metrics.faculty_adequacy,
            'Placement_Rate': metrics.placement_rate,
            'Infrastructure_Quality': metrics.infrastructure_quality,
            'Financial_Efficiency': metrics.financial_efficiency,
            'Fund_Utilization': metrics.fund_utilization,
            'Avg_Doc_DSS': metrics.avg_doc_dss,
            'Missing_Doc_Count': metrics.missing_doc_count,
            'Total_Students': metrics.total_students,
            'Total_Faculty': metrics.total_faculty
        }
        
        prediction = predictor.predict_performance_tier(features)
        
        if 'error' in prediction:
            raise HTTPException(status_code=400, detail=prediction['error'])
        
        # Calculate overall score (simplified for demo)
        overall_score = (
            metrics.placement_rate * 0.25 +
            metrics.faculty_adequacy * 0.20 +
            metrics.infrastructure_quality * 0.20 +
            metrics.financial_efficiency * 0.15 +
            metrics.avg_doc_dss * 0.20
        )
        
        return PerformanceTierResponse(
            college_name=metrics.college_name,
            performance_tier=prediction['performance_tier'],
            confidence=prediction['confidence'],
            overall_score=overall_score
        )
    except Exception as e:
        logger.error(f"Performance prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/anomaly", response_model=AnomalyDetectionResponse, tags=["Predictions"])
async def detect_anomaly(metrics: InstitutionMetrics):
    """
    Detect if institution is anomalous
    
    Args:
        metrics: Institution metrics
        
    Returns:
        AnomalyDetectionResponse with anomaly detection result
    """
    if not ML_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML models not available")
    
    try:
        features = {
            'Student_Faculty_Ratio': metrics.student_faculty_ratio,
            'Faculty_Adequacy': metrics.faculty_adequacy,
            'Placement_Rate': metrics.placement_rate,
            'Infrastructure_Quality': metrics.infrastructure_quality,
            'Financial_Efficiency': metrics.financial_efficiency,
            'Fund_Utilization': metrics.fund_utilization,
            'Avg_Doc_DSS': metrics.avg_doc_dss,
            'Missing_Doc_Count': metrics.missing_doc_count,
            'Total_Students': metrics.total_students,
            'Total_Faculty': metrics.total_faculty
        }
        
        prediction = predictor.detect_anomalies(features)
        
        if 'error' in prediction:
            raise HTTPException(status_code=400, detail=prediction['error'])
        
        return AnomalyDetectionResponse(
            college_name=metrics.college_name,
            is_anomalous=prediction['is_anomaly'],
            anomaly_score=prediction['anomaly_score'],
            status=prediction['status']
        )
    except Exception as e:
        logger.error(f"Anomaly detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate/institution", response_model=ComprehensiveScoreResponse, tags=["Evaluation"])
async def evaluate_institution(metrics: InstitutionMetrics):
    """
    Comprehensive institutional evaluation
    
    Combines all predictions into a single score
    
    Args:
        metrics: Institution metrics
        
    Returns:
        ComprehensiveScoreResponse with complete evaluation
    """
    if not ML_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML models not available")
    
    try:
        features = {
            'Student_Faculty_Ratio': metrics.student_faculty_ratio,
            'Faculty_Adequacy': metrics.faculty_adequacy,
            'Placement_Rate': metrics.placement_rate,
            'Infrastructure_Quality': metrics.infrastructure_quality,
            'Financial_Efficiency': metrics.financial_efficiency,
            'Fund_Utilization': metrics.fund_utilization,
            'Avg_Doc_DSS': metrics.avg_doc_dss,
            'Missing_Doc_Count': metrics.missing_doc_count,
            'Total_Students': metrics.total_students,
            'Total_Faculty': metrics.total_faculty
        }
        
        # Calculate overall score
        overall_score = (
            metrics.placement_rate * 0.25 +
            metrics.faculty_adequacy * 0.20 +
            metrics.infrastructure_quality * 0.20 +
            metrics.financial_efficiency * 0.15 +
            metrics.avg_doc_dss * 0.20
        )
        
        # Get all predictions
        risk_pred = predictor.predict_risk_level(features)
        perf_pred = predictor.predict_performance_tier(features)
        anomaly_pred = predictor.detect_anomalies(features)
        
        metrics_dict = {
            'placement_score': metrics.placement_rate,
            'faculty_score': metrics.faculty_adequacy,
            'infrastructure_score': metrics.infrastructure_quality,
            'financial_score': metrics.financial_efficiency,
            'compliance_score': metrics.avg_doc_dss,
            'overall_score': overall_score
        }
        
        return ComprehensiveScoreResponse(
            college_name=metrics.college_name,
            overall_score=overall_score,
            metrics=metrics_dict,
            risk_assessment=risk_pred,
            performance_tier=perf_pred,
            anomaly_detection=anomaly_pred,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Institution evaluation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

@app.post("/batch/evaluate", tags=["Batch Operations"])
async def batch_evaluate(institutions: List[InstitutionMetrics]):
    """
    Evaluate multiple institutions in batch
    
    Args:
        institutions: List of institutions to evaluate
        
    Returns:
        List of evaluation results
    """
    if not ML_AVAILABLE:
        raise HTTPException(status_code=503, detail="ML models not available")
    
    try:
        results = []
        for metrics in institutions:
            features = {
                'Student_Faculty_Ratio': metrics.student_faculty_ratio,
                'Faculty_Adequacy': metrics.faculty_adequacy,
                'Placement_Rate': metrics.placement_rate,
                'Infrastructure_Quality': metrics.infrastructure_quality,
                'Financial_Efficiency': metrics.financial_efficiency,
                'Fund_Utilization': metrics.fund_utilization,
                'Avg_Doc_DSS': metrics.avg_doc_dss,
                'Missing_Doc_Count': metrics.missing_doc_count,
                'Total_Students': metrics.total_students,
                'Total_Faculty': metrics.total_faculty
            }
            
            overall_score = (
                metrics.placement_rate * 0.25 +
                metrics.faculty_adequacy * 0.20 +
                metrics.infrastructure_quality * 0.20 +
                metrics.financial_efficiency * 0.15 +
                metrics.avg_doc_dss * 0.20
            )
            
            result = {
                'college_name': metrics.college_name,
                'overall_score': overall_score,
                'risk_assessment': predictor.predict_risk_level(features),
                'performance_tier': predictor.predict_performance_tier(features),
                'anomaly_detection': predictor.detect_anomalies(features)
            }
            results.append(result)
        
        return results
    except Exception as e:
        logger.error(f"Batch evaluation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# ROOT & INFO
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "EduTrack API",
        "version": "1.0.0",
        "description": "Institutional Evaluation and Risk Assessment System",
        "docs": "/docs",
        "ml_available": ML_AVAILABLE
    }


@app.get("/info", tags=["Info"])
async def info():
    """API information endpoint"""
    return {
        "system": "EduTrack",
        "version": "1.0.0",
        "status": "operational" if ML_AVAILABLE else "degraded",
        "features": [
            "Risk Assessment",
            "Performance Tier Prediction",
            "Anomaly Detection",
            "Batch Evaluation",
            "Comprehensive Scoring"
        ],
        "endpoints": [
            "/docs",
            "/health",
            "/predict/risk",
            "/predict/performance",
            "/predict/anomaly",
            "/evaluate/institution",
            "/batch/evaluate"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
