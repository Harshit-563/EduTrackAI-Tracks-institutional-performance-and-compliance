from __future__ import annotations

from sqlalchemy.orm import Session


class UnitOfWork:
    def __init__(self, db: Session):
        self.db = db

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.db.rollback()
            return False
        self.db.commit()
        return False
