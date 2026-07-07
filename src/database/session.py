from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from src.core.config import settings


is_sqlite = settings.database_url.startswith("sqlite")

engine_kwargs = {
    "echo": settings.debug,
    "future": True,
    "connect_args": {"check_same_thread": False} if is_sqlite else {},
}
if not is_sqlite:
    engine_kwargs["poolclass"] = QueuePool
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(settings.database_url, **engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    from src.database.models import Base

    Base.metadata.create_all(bind=engine)
