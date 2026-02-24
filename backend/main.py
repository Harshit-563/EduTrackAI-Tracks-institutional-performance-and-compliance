from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import tempfile
import os
import sys

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

try:
    from doc_validator.ocr_engine import run_ocr
    from doc_validator.predictor import predict_from_ocr
except Exception:
    run_ocr = None
    predict_from_ocr = None

app = FastAPI(title="EduTrack Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USERS = [
    {"email": "principal.techno@college.test", "password": "test123", "role": "institution"},
    {"email": "reviewer.ramesh@aicte-review.test", "password": "test123", "role": "reviewer"},
    {"email": "superadmin@edutrack.test", "password": "admin123", "role": "admin"},
]

SUBMISSIONS: List[Dict[str, Any]] = [
    {
        "id": "SUB-101",
        "institution": "North Valley Institute",
        "institution_id": "inst_demo",
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
        "institution_id": "inst_demo",
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
]

TOKENS: Dict[str, Dict[str, str]] = {}


class LoginPayload(BaseModel):
    email: str
    password: str


class ReviewActionPayload(BaseModel):
    action: str
    notes: Optional[str] = None


def _issue_token(email: str, role: str) -> str:
    raw = f"{email}:{role}:{datetime.utcnow().isoformat()}"
    token = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    TOKENS[token] = {"email": email, "role": role}
    return token


def _read_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        return None
    return authorization[len(prefix) :].strip()


def _require_auth(authorization: Optional[str]) -> Dict[str, str]:
    token = _read_bearer(authorization)
    if token == "local-dev-token":
        return {"email": "local.dev@edutrack.test", "role": "institution"}
    if not token or token not in TOKENS:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return TOKENS[token]


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login")
def login(payload: LoginPayload) -> Dict[str, Any]:
    for user in USERS:
        if user["email"] == payload.email and user["password"] == payload.password:
            token = _issue_token(user["email"], user["role"])
            return {
                "token": token,
                "user": {"email": user["email"], "role": user["role"]},
                "expires_in": int(timedelta(hours=12).total_seconds()),
            }
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/auth/me")
def me(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    user = _require_auth(authorization)
    return {"user": user}


@app.get("/reviewer/queue")
def reviewer_queue(authorization: Optional[str] = Header(default=None)) -> List[Dict[str, Any]]:
    _require_auth(authorization)
    return SUBMISSIONS


@app.get("/reviewer/document/{submission_id}")
def reviewer_document(submission_id: str, authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    _require_auth(authorization)
    for item in SUBMISSIONS:
        if item["id"] == submission_id:
            return item
    raise HTTPException(status_code=404, detail="Submission not found")


@app.post("/reviews/{submission_id}/action")
def review_action(
    submission_id: str,
    payload: ReviewActionPayload,
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_auth(authorization)
    for item in SUBMISSIONS:
        if item["id"] == submission_id:
            item["status"] = payload.action
            item["review_note"] = payload.notes or ""
            return {"ok": True, "submission": item}
    raise HTTPException(status_code=404, detail="Submission not found")


@app.post("/upload-analyze")
async def upload_analyze(
    file: UploadFile = File(...),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_auth(authorization)

    file_suffix = Path(file.filename or "upload.bin").suffix or ".bin"

    # Use your existing root/doc_validator pipeline when available.
    dss_score = 70
    flags: List[str] = []
    extracted_fields: Dict[str, Any] = {}

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_suffix) as tmp:
        tmp_path = tmp.name
        content = await file.read()
        tmp.write(content)

    try:
        if run_ocr and predict_from_ocr:
            ocr_output = run_ocr(tmp_path)
            if isinstance(ocr_output, dict):
                ocr_output["doc_type"] = "uploaded_document"

            prediction = predict_from_ocr(ocr_output)
            if isinstance(prediction, dict):
                dss_score = int(prediction.get("dss_score", dss_score))
                flags = list(prediction.get("dss_flags", []))
                extracted_fields = prediction.get("fields", {}) or {}
        else:
            flags.append("Predictor module unavailable; using fallback DSS")
    except Exception as exc:
        flags.append(f"Pipeline fallback: {str(exc)}")
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    submission_id = f"SUB-{100 + len(SUBMISSIONS) + 1}"
    today = datetime.utcnow().date().isoformat()

    new_item = {
        "id": submission_id,
        "institution": "Demo Institute",
        "institution_id": "demo",
        "doc_type": "uploaded_document",
        "dss": max(0, min(100, dss_score)),
        "status": "parsed" if not flags else "needs_manual_review",
        "uploaded_at": today,
        "flags": flags,
        "extracted_fields": extracted_fields,
    }
    SUBMISSIONS.insert(0, new_item)

    return {
        "submission_id": submission_id,
        "file_name": file.filename,
        "dss": new_item["dss"],
        "compliance": "Compliant" if new_item["dss"] >= 75 else "Needs Correction",
        "fields": new_item["extracted_fields"],
        "flags": new_item["flags"],
    }


@app.get("/institutions/{institution_id}/submissions")
def institution_submissions(
    institution_id: str,
    authorization: Optional[str] = Header(default=None),
) -> List[Dict[str, Any]]:
    _require_auth(authorization)
    return [s for s in SUBMISSIONS if s.get("institution_id") in {institution_id, "inst_demo", "demo"}]


@app.get("/institutions/{institution_id}/overview")
def institution_overview(
    institution_id: str,
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_auth(authorization)
    rows = [s for s in SUBMISSIONS if s.get("institution_id") in {institution_id, "inst_demo", "demo"}]
    avg_dss = round(sum(float(r.get("dss", 0)) for r in rows) / len(rows), 1) if rows else 0.0
    pending = sum(1 for r in rows if r.get("status") in {"needs_manual_review", "low_confidence"})
    compliance = max(0, min(100, round(avg_dss - pending * 2, 1)))

    return {
        "institution_name": "Demo Institute of Technology",
        "avg_dss": avg_dss,
        "compliance": compliance,
        "pending_reviews": pending,
    }


@app.get("/institutions/{institution_id}/dss-trend")
def institution_dss_trend(
    institution_id: str,
    authorization: Optional[str] = Header(default=None),
) -> List[Dict[str, Any]]:
    _require_auth(authorization)
    return [
        {"year": "2022", "dss": 62},
        {"year": "2023", "dss": 68},
        {"year": "2024", "dss": 71},
        {"year": "2025", "dss": 74},
        {"year": "2026", "dss": 79},
    ]

