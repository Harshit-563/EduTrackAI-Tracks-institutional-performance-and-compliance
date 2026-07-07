"""
Database initialization and sample data script for development environments.
"""

from src.auth.utils import hash_password
from src.database import SessionLocal, init_db
from src.database.models import DocumentStatus, UserRole
from src.database.repositories import DocumentRepository, InstitutionRepository, UserRepository


def populate_sample_data():
    db = SessionLocal()
    try:
        inst_repo = InstitutionRepository(db)
        institutions = [
            {
                "name": "North Valley Institute",
                "total_students": 1200,
                "total_faculty": 38,
                "placement_rate": 62,
                "fund_utilization": 78,
                "infrastructure_area": 4200,
            },
            {
                "name": "Delta Technical Campus",
                "total_students": 1600,
                "total_faculty": 30,
                "placement_rate": 48,
                "fund_utilization": 85,
                "infrastructure_area": 3900,
            },
            {
                "name": "Metro College of Engineering",
                "total_students": 2100,
                "total_faculty": 74,
                "placement_rate": 71,
                "fund_utilization": 80,
                "infrastructure_area": 6400,
            },
            {
                "name": "Westbridge Institute",
                "total_students": 900,
                "total_faculty": 42,
                "placement_rate": 82,
                "fund_utilization": 91,
                "infrastructure_area": 4600,
            },
        ]

        inst_ids = {}
        for institution_data in institutions:
            existing = inst_repo.get_by_name(institution_data["name"])
            institution = existing or inst_repo.create(**institution_data)
            inst_ids[institution_data["name"]] = institution.id

        user_repo = UserRepository(db)
        users = [
            {
                "email": "principal.techno@college.test",
                "password_hash": hash_password("test123"),
                "role": UserRole.INSTITUTION.value,
                "institution_id": inst_ids["North Valley Institute"],
            },
            {
                "email": "reviewer.ramesh@aicte-review.test",
                "password_hash": hash_password("test123"),
                "role": UserRole.REVIEWER.value,
            },
            {
                "email": "superadmin@edutrack.test",
                "password_hash": hash_password("admin123"),
                "role": UserRole.ADMIN.value,
            },
        ]

        user_ids = {}
        for user_data in users:
            existing = user_repo.get_by_email(user_data["email"])
            user = existing or user_repo.create(**user_data)
            user_ids[user.email] = user.id

        doc_repo = DocumentRepository(db)
        documents = [
            {
                "submission_code": "SUB-101",
                "institution_id": inst_ids["North Valley Institute"],
                "doc_type": "fire_safety_certificate",
                "original_filename": "fire_safety_certificate.pdf",
                "dss_score": 91,
                "compliance_score": 88,
                "status": DocumentStatus.NEEDS_MANUAL_REVIEW,
                "uploaded_by": user_ids["principal.techno@college.test"],
                "flags": ["Expiry date found", "Signature confidence medium"],
                "extracted_fields": {
                    "certificate_no": "FS-2026-0092",
                    "valid_till": "2027-12-31",
                    "authority": "City Fire Department",
                },
                "classification_label": "fire_safety_certificate",
                "classification_confidence": 0.94,
            },
            {
                "submission_code": "SUB-102",
                "institution_id": inst_ids["Delta Technical Campus"],
                "doc_type": "financial_audit",
                "original_filename": "financial_audit.pdf",
                "dss_score": 58,
                "compliance_score": 52,
                "status": DocumentStatus.LOW_CONFIDENCE,
                "uploaded_by": user_ids["principal.techno@college.test"],
                "flags": ["Stamp missing", "Auditor signature unclear"],
                "extracted_fields": {
                    "fiscal_year": "2024-25",
                    "auditor": "M/S K Sharma & Co.",
                },
                "classification_label": "financial_audit",
                "classification_confidence": 0.88,
            },
        ]

        for document_data in documents:
            if not doc_repo.get_by_code(document_data["submission_code"]):
                doc_repo.create(**document_data)

        db.commit()
        return True
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    populate_sample_data()
