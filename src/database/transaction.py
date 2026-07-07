from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy.orm import Session


@contextmanager
def transactional(db: Session) -> Iterator[None]:
    try:
        yield
        db.commit()
    except Exception:
        db.rollback()
        raise
