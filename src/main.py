"""
FastAPI Application for EduTrack Backend
Handles: Authentication, Document Upload, Submissions, Rankings

Fixed Issues:
- Typo: OCIR_AVAILABLE → OCR_AVAILABLE
- Added input validation with Pydantic validators
- Better error handling
- Added pagination support
- Improved logging
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import csv
import tempfile
import os
import sys
import logging

from fastapi import FastAPI, File, Header, HTTPException, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, validator
from dotenv import load_dotenv

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Import utilities
from utils.logger import setup_logger
from utils.constants import EVALUATION_WEIGHTS, REQUIRED_DOCUMENTS

# Setup logging
logger = setup_logger(__name__)
load_dotenv()

# Try importing ML modules (graceful fallback if unavailable)
try:
    from doc_validator.ocr_engine import run_ocr
    from doc_validator.predictor import predict_from_ocr
    OCR_AVAILABLE = True  # ✅ FIXED: Was OCIR_AVAILABLE
    logger.info("✓ OCR pipeline loaded successfully")
except ImportError as e:
    logger.warning(f"✗ OCR pipeline unavailable: {e}")
    run_ocr = None
    predict_from_ocr = None
    OCR_AVAILABLE = False

try:
    from risk_engine import predict_risk
    RISK_MODEL_AVAILABLE = True
    logger.info("✓ Risk model loaded successfully")
except ImportError as e:
    logger.warning(f"✗ Risk model unavailable: {e}")
    predict_risk = None
    RISK_MODEL_AVAILABLE = False

# =====================================================
# CONFIGURATION & CONSTANTS
# =====================================================

ALLOWED_UPLOADS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff"}
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_SUBMISSIONS_PER_PAGE = 50

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://localhost:8080",
]

# =====================================================
# PYDANTIC MODELS (WITH VALIDATORS)
# =====================================================

class LoginPayload(BaseModel):
    """User login credentials"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")

    @validator('email')
    def email_must_be_valid(cls, v):
        """Validate email format"""
        if '@' not in v or len(v) < 5:
            raise ValueError('Invalid email format')
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "email": "principal@college.test",
                "password": "test123"
            }
        }


class ReviewActionPayload(BaseModel):
    """Review action for document submission"""
    action: str = Field(..., description="Action: approved, rejected, needs_manual_review")
    notes: Optional[str] = Field(None, max_length=500, description="Reviewer notes")

    @validator('action')
    def validate_action(cls, v):
        """Validate action is one of allowed values"""
        allowed = {"approved", "rejected", "needs_manual_review"}
        if v not in allowed:
            raise ValueError(f'Action must be one of: {allowed}')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "action": "needs_manual_review",
                "notes": "Signature verification required"
            }
        }


class UserResponse(BaseModel):
    """User response model"""
    email: str
    role: str


class TokenResponse(BaseModel):
    """Login token response"""
    token: str
    user: UserResponse
    expires_in: int


class PaginationParams(BaseModel):
    """Pagination parameters"""
    limit: int = Field(default=10, ge=1, le=MAX_SUBMISSIONS_PER_PAGE)
    offset: int = Field(default=0, ge=0)


# =====================================================
# USER & AUTHENTICATION DATA
# =====================================================

# TODO: Move to database (SQLAlchemy + PostgreSQL)
USERS = [
    {"email": "principal.techno@college.test", "password": "test123", "role": "institution"},
    {"email": "reviewer.ramesh@aicte-review.test", "password": "test123", "role": "reviewer"},
    {"email": "superadmin@edutrack.test", "password": "admin123", "role": "admin"},
]

TOKENS: Dict[str, Dict[str, str]] = {}

# =====================================================
# INSTITUTIONAL DATA (TEMPORARY - MOVE TO DATABASE)
# =====================================================

INSTITUTION_PROFILES: Dict[str, Dict[str, float]] = {
    "North Valley Institute": {
        "Total_Students": 1200,
        "Total_Faculty": 38,
        "Placement_Rate": 62,
        "Fund_Utilization": 78,
        "Infrastructure_Area": 4200,
    },
    "Delta Technical Campus": {
        "Total_Students": 1600,
        "Total_Faculty": 30,
        "Placement_Rate": 48,
        "Fund_Utilization": 85,
        "Infrastructure_Area": 3900,
    },
    "Metro College of Engineering": {
        "Total_Students": 2100,
        "Total_Faculty": 74,
        "Placement_Rate": 71,
        "Fund_Utilization": 80,
        "Infrastructure_Area": 6400,
    },
    "Westbridge Institute": {
        "Total_Students": 900,
        "Total_Faculty": 42,
        "Placement_Rate": 82,
        "Fund_Utilization": 91,
        "Infrastructure_Area": 4600,
    },
}

SUBMISSIONS: List[Dict[str, Any]] = [
    {
        "id": "SUB-101",
        "institution": "North Valley Institute",
        "institution_id": "inst_001",
        "doc_type": "fire_safety_certificate",
        "dss": 91,
        "status": "needs_manual_review",
        "uploaded_at": "2026-01-19",
        "flags": ["Expiry date found", "Signature confidence medium"],
        "extracted_fields": {
            "certificate_no": "FS-2026-0092",
            "valid_till": "2027-12-31",
            "authority": "City Fire Department",
        },
    },
    {
        "id": "SUB-102",
        "institution": "Delta Technical Campus",
        "institution_id": "inst_002",
        "doc_type": "financial_audit",
        "dss": 58,
        "status": "low_confidence",
        "uploaded_at": "2026-01-17",
        "flags": ["Stamp missing", "Auditor signature unclear"],
        "extracted_fields": {
            "fiscal_year": "2024-25",
            "auditor": "M/S K Sharma & Co.",
        },
    },
    {
        "id": "SUB-103",
        "institution": "Metro College of Engineering",
        "institution_id": "inst_003",
        "doc_type": "faculty_list",
        "dss": 84,
        "status": "parsed",
        "uploaded_at": "2026-01-16",
        "flags": [],
        "extracted_fields": {
            "faculty_count": 126,
            "phd_count": 48,
        },
    },
    {
        "id": "SUB-104",
        "institution": "Westbridge Institute",
        "institution_id": "inst_004",
        "doc_type": "affiliation_letter",
        "dss": 96,
        "status": "approved",
        "uploaded_at": "2026-01-11",
        "flags": [],
        "extracted_fields": {
            "affiliation_id": "UGC-AFF-2026-781",
            "valid_till": "2028-03-31",
        },
    },
]

# =====================================================
# FastAPI APP INITIALIZATION
# =====================================================

app = FastAPI(
    title="EduTrack Backend API",
    description="AI-Based Institutional Compliance & Risk System",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def _issue_token(email: str, role: str) -> str:
    """Issue authentication token"""
    raw = f"{email}:{role}:{datetime.utcnow().isoformat()}"
    token = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    TOKENS[token] = {"email": email, "role": role}
    logger.info(f"Token issued for {email} (role: {role})")
    return token


def _read_bearer(authorization: Optional[str]) -> Optional[str]:
    """Extract bearer token from Authorization header"""
    if not authorization:
        return None
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return None
    return authorization[len(prefix):].strip()


def _require_auth(authorization: Optional[str]) -> Dict[str, str]:
    """Validate authentication and return user info"""
    token = _read_bearer(authorization)
    
    # Allow local dev token
    if token == "local-dev-token":
        logger.debug("Using local dev token")
        return {"email": "local.dev@edutrack.test", "role": "institution"}
    
    if not token or token not in TOKENS:
        logger.warning(f"Unauthorized access attempt")
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing token")
    
    return TOKENS[token]


def _validate_file_upload(file: UploadFile) -> None:
    """Validate uploaded file"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_UPLOADS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_UPLOADS)}"
        )


def _fallback_risk_score(avg_dss: float, missing_docs: int) -> float:
    """Fallback risk scoring when ML model unavailable"""
    base = 100.0 - avg_dss
    penalty = min(30.0, missing_docs * 8.0)
    score = max(0.0, min(100.0, base + penalty))
    return round(score, 2)


def _compute_institution_risk_score(
    institution_name: str,
    avg_dss: float,
    missing_docs: int
) -> float:
    """Compute risk score using ML model or fallback"""
    if not RISK_MODEL_AVAILABLE:
        logger.debug(f"Using fallback risk scoring for {institution_name}")
        return _fallback_risk_score(avg_dss, missing_docs)

    profile = INSTITUTION_PROFILES.get(institution_name)
    if not profile:
        logger.warning(f"Institution profile not found: {institution_name}")
        return _fallback_risk_score(avg_dss, missing_docs)

    payload = {
        **profile,
        "Avg_Doc_DSS": avg_dss,
        "Missing_Doc_Count": missing_docs,
    }

    try:
        result = predict_risk(payload)
        if isinstance(result, dict):
            score = result.get("risk_score")
            if isinstance(score, (int, float)):
                return round(float(score), 2)
    except Exception as exc:
        logger.error(f"Risk prediction failed for {institution_name}: {exc}")

    return _fallback_risk_score(avg_dss, missing_docs)


def _build_institution_rank_list() -> List[Dict[str, Any]]:
    """Build ranked list of institutions from submissions"""
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    
    for row in SUBMISSIONS:
        institution = row.get("institution", "Unknown")
        grouped.setdefault(institution, []).append(row)

    rank_rows: List[Dict[str, Any]] = []
    
    for institution, rows in grouped.items():
        dss_values = [float(r.get("dss", 0.0)) for r in rows]
        avg_dss = round(sum(dss_values) / len(dss_values), 2) if dss_values else 0.0
        
        missing_docs = sum(
            1 for r in rows
            if r.get("status") in {"needs_manual_review", "low_confidence"}
        )

        risk_score = _compute_institution_risk_score(institution, avg_dss, missing_docs)
        rank_score = round((avg_dss + (100 - risk_score)) / 2.0, 2)

        rank_rows.append({
            "institution": institution,
            "avg_dss_score": avg_dss,
            "risk_score": risk_score,
            "rank_score": rank_score,
            "submission_count": len(rows),
        })

    rank_rows.sort(key=lambda r: r["rank_score"], reverse=True)
    for idx, row in enumerate(rank_rows, start=1):
        row["rank"] = idx

    return rank_rows


def _load_rank_list_from_csv() -> List[Dict[str, Any]]:
    """Load pre-computed rankings from CSV"""
    csv_path = PROJECT_ROOT / "college_rank_list.csv"
    
    if not csv_path.exists():
        logger.debug("Rank list CSV not found, using computed rankings")
        return []

    rows: List[Dict[str, Any]] = []
    
    try:
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader is None:
                logger.warning("CSV file is empty")
                return []
            
            for raw in reader:
                try:
                    rows.append({
                        "rank": int(float(raw.get("Rank", 0) or 0)),
                        "institution": str(raw.get("College Name", "")).strip(),
                        "avg_dss_score": round(float(raw.get("Avg_Doc_DSS", 0) or 0), 2),
                        "risk_score": round(float(raw.get("Risk_Score", 0) or 0), 2),
                        "rank_score": round(float(raw.get("Rank_Score", 0) or 0), 2),
                        "submission_count": None,
                    })
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to parse rank row: {e}")
                    continue
    except Exception as e:
        logger.error(f"Failed to load rank list CSV: {e}")
        return []

    rows.sort(key=lambda r: r.get("rank", 10**9))
    logger.info(f"Loaded {len(rows)} rankings from CSV")
    return rows


# =====================================================
# HEALTH & AUTH ENDPOINTS
# =====================================================

@app.get("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "ok",
        "ocr_available": OCR_AVAILABLE,  # ✅ FIXED
        "risk_model_available": RISK_MODEL_AVAILABLE,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginPayload) -> Dict[str, Any]:
    """Authenticate user and issue token"""
    logger.info(f"Login attempt for {payload.email}")
    
    try:
        for user in USERS:
            if user["email"] == payload.email and user["password"] == payload.password:
                token = _issue_token(user["email"], user["role"])
                return {
                    "token": token,
                    "user": {"email": user["email"], "role": user["role"]},
                    "expires_in": int(timedelta(hours=12).total_seconds()),
                }
        
        logger.warning(f"Failed login for {payload.email}: Invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")


@app.get("/auth/me", response_model=Dict[str, UserResponse])
def me(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    """Get current user info"""
    try:
        user = _require_auth(authorization)
        return {"user": user}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user info: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch user info")


# =====================================================
# REVIEWER ENDPOINTS
# =====================================================

@app.get("/reviewer/queue")
def reviewer_queue(
    authorization: Optional[str] = Header(default=None),
    limit: int = Query(10, ge=1, le=MAX_SUBMISSIONS_PER_PAGE),
    offset: int = Query(0, ge=0),
) -> Dict[str, Any]:
    """Get paginated queue of documents for review"""
    try:
        _require_auth(authorization)
        logger.info(f"Reviewer accessing document queue (limit={limit}, offset={offset})")
        
        total = len(SUBMISSIONS)
        items = SUBMISSIONS[offset:offset + limit]
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": items,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving queue: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve queue")


@app.get("/reviewer/document/{submission_id}")
def reviewer_document(
    submission_id: str,
    authorization: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """Get specific document for review"""
    try:
        _require_auth(authorization)
        
        for item in SUBMISSIONS:
            if item["id"] == submission_id:
                logger.info(f"Retrieved submission {submission_id}")
                return item
        
        logger.warning(f"Submission not found: {submission_id}")
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving document: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve document")


@app.post("/reviews/{submission_id}/action")
def review_action(
    submission_id: str,
    payload: ReviewActionPayload,
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """Submit review action on document"""
    try:
        user = _require_auth(authorization)
        
        for item in SUBMISSIONS:
            if item["id"] == submission_id:
                item["status"] = payload.action
                item["review_note"] = payload.notes or ""
                item["reviewed_by"] = user["email"]
                item["reviewed_at"] = datetime.utcnow().isoformat()
                
                logger.info(f"Review submitted for {submission_id} by {user['email']}: {payload.action}")
                return {"ok": True, "submission": item}
        
        logger.warning(f"Submission not found for review: {submission_id}")
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting review: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit review")


# =====================================================
# DOCUMENT UPLOAD & ANALYSIS
# =====================================================

@app.post("/upload-analyze")
async def upload_analyze(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """Upload and analyze document"""
    user = _require_auth(authorization)
    
    # Validate file
    _validate_file_upload(file)
    
    logger.info(f"Document upload initiated by {user['email']}: {file.filename}")
    
    # Initialize defaults
    dss_score = 70
    flags: List[str] = []
    extracted_fields: Dict[str, Any] = {}
    file_suffix = Path(file.filename).suffix or ".bin"

    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp:
        tmp_path = tmp.name
        try:
            content = await file.read()
            if not content:
                raise HTTPException(status_code=400, detail="Uploaded file is empty")
            tmp.write(content)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to write temporary file: {e}")
            raise HTTPException(status_code=500, detail="Upload processing failed")

    try:
        # Run OCR pipeline if available
        if OCR_AVAILABLE and run_ocr and predict_from_ocr:  # ✅ FIXED
            try:
                ocr_output = run_ocr(tmp_path)
                if isinstance(ocr_output, dict):
                    ocr_output["doc_type"] = "uploaded_document"

                prediction = predict_from_ocr(ocr_output)
                if isinstance(prediction, dict):
                    dss_score = int(prediction.get("dss_score", dss_score))
                    flags = list(prediction.get("dss_flags", []))
                    extracted_fields = prediction.get("fields", {}) or {}
                    logger.info(f"OCR pipeline executed successfully (DSS: {dss_score})")
            except Exception as exc:
                logger.error(f"OCR pipeline error: {exc}")
                flags.append(f"OCR processing failed: {str(exc)}")
        else:
            flags.append("OCR pipeline unavailable; using baseline DSS")
            logger.warning("OCR pipeline not available, using baseline scoring")
    
    finally:
        try:
            os.remove(tmp_path)
        except Exception as e:
            logger.warning(f"Failed to remove temporary file: {e}")

    # Create submission record
    submission_id = f"SUB-{100 + len(SUBMISSIONS) + 1}"
    today = datetime.utcnow().date().isoformat()

    new_item = {
        "id": submission_id,
        "institution": "Demo Institute",
        "institution_id": "inst_demo",
        "doc_type": "uploaded_document",
        "dss": max(0, min(100, dss_score)),
        "status": "parsed" if not flags else "needs_manual_review",
        "uploaded_at": today,
        "uploaded_by": user["email"],
        "flags": flags,
        "extracted_fields": extracted_fields,
    }
    SUBMISSIONS.insert(0, new_item)

    logger.info(f"Document analysis completed: {submission_id} (DSS: {new_item['dss']})")

    return {
        "submission_id": submission_id,
        "file_name": file.filename,
        "dss": new_item["dss"],
        "compliance": "Compliant" if new_item["dss"] >= 75 else "Needs Correction",
        "fields": new_item["extracted_fields"],
        "flags": new_item["flags"],
    }


# =====================================================
# INSTITUTION ENDPOINTS
# =====================================================

@app.get("/institutions/{institution_id}/submissions")
def institution_submissions(
    institution_id: str,
    authorization: Optional[str] = Header(default=None),
    limit: int = Query(10, ge=1, le=MAX_SUBMISSIONS_PER_PAGE),
    offset: int = Query(0, ge=0),
) -> Dict[str, Any]:
    """Get paginated submissions for institution"""
    try:
        _require_auth(authorization)
        
        results = [
            s for s in SUBMISSIONS
            if s.get("institution_id") in {institution_id, "inst_demo", "demo"}
        ]
        
        total = len(results)
        items = results[offset:offset + limit]
        
        logger.info(f"Retrieved {len(items)} of {total} submissions for {institution_id}")
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "items": items,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving submissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve submissions")


@app.get("/institutions/{institution_id}/overview")
def institution_overview(
    institution_id: str,
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    """Get institution overview and compliance metrics"""
    try:
        _require_auth(authorization)
        
        rows = [
            s for s in SUBMISSIONS
            if s.get("institution_id") in {institution_id, "inst_demo", "demo"}
        ]
        
        if not rows:
            return {
                "institution_id": institution_id,
                "institution_name": "Unknown Institution",
                "avg_dss": 0,
                "compliance": 0,
                "pending_reviews": 0,
                "total_submissions": 0,
            }
        
        avg_dss = round(sum(float(r.get("dss", 0)) for r in rows) / len(rows), 1)
        pending = sum(1 for r in rows if r.get("status") in {"needs_manual_review", "low_confidence"})
        compliance = max(0, min(100, round(avg_dss - pending * 2, 1)))

        result = {
            "institution_id": institution_id,
            "institution_name": "Demo Institute of Technology",
            "avg_dss": avg_dss,
            "compliance": compliance,
            "pending_reviews": pending,
            "total_submissions": len(rows),
        }
        
        logger.info(f"Overview retrieved for {institution_id}")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve overview")


@app.get("/institutions/{institution_id}/dss-trend")
def institution_dss_trend(
    institution_id: str,
    authorization: Optional[str] = Header(default=None),
) -> List[Dict[str, Any]]:
    """Get DSS trend over years"""
    try:
        _require_auth(authorization)
        
        logger.info(f"DSS trend retrieved for {institution_id}")
        
        return [
            {"year": "2022", "dss": 62},
            {"year": "2023", "dss": 68},
            {"year": "2024", "dss": 71},
            {"year": "2025", "dss": 74},
            {"year": "2026", "dss": 79},
        ]
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving trend: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trend")


@app.get("/institutions/rank-list")
def institutions_rank_list(
    authorization: Optional[str] = Header(default=None)
) -> Dict[str, Any]:
    """Get institution rankings"""
    try:
        _require_auth(authorization)
        
        # Try loading from CSV first
        csv_rows = _load_rank_list_from_csv()
        if csv_rows:
            logger.info("Returning rankings from CSV")
            return {
                "count": len(csv_rows),
                "source": "college_rank_list.csv",
                "items": csv_rows,
            }

        # Fall back to computed rankings
        rows = _build_institution_rank_list()
        logger.info(f"Returning {len(rows)} computed rankings")
        return {
            "count": len(rows),
            "source": "computed_from_submissions",
            "items": rows,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving rankings: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve rankings")


# =====================================================
# ERROR HANDLERS
# =====================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    logger.error(f"HTTP Error {exc.status_code}: {exc.detail}")
    return {"error": exc.detail, "status_code": exc.status_code}


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unexpected error: {exc}")
    return {"error": "Internal server error", "status_code": 500}
