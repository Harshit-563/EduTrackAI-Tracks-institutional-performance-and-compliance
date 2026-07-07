from typing import Any, Dict, List

USERS: List[Dict[str, Any]] = [
    {"email": "principal.techno@college.test", "password": "test123", "role": "institution"},
    {"email": "reviewer.ramesh@aicte-review.test", "password": "test123", "role": "reviewer"},
    {"email": "superadmin@edutrack.test", "password": "admin123", "role": "admin"},
]

TOKENS: Dict[str, Dict[str, str]] = {}

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
