from __future__ import annotations

from sqlalchemy import inspect
from sqlalchemy.orm import Session


class SchemaValidationService:
    def __init__(self, db: Session):
        self.db = db

    def validate_required_tables(self) -> dict[str, bool]:
        inspector = inspect(self.db.bind)
        existing_tables = set(inspector.get_table_names())
        required_tables = {
            "users": "users" in existing_tables,
            "institutions": "institutions" in existing_tables,
            "documents": "documents" in existing_tables,
            "compliance_rules": "compliance_rules" in existing_tables,
            "review_actions": "review_actions" in existing_tables,
            "ai_predictions": "ai_predictions" in existing_tables,
            "reports": "reports" in existing_tables,
            "notifications": "notifications" in existing_tables,
            "audit_logs": "audit_logs" in existing_tables,
        }
        return required_tables
