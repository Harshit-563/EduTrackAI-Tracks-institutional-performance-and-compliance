from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import secrets


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    project_name: str
    api_version: str
    environment: str
    debug: bool
    project_root: Path
    api_prefix: str
    database_url: str
    secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    cors_origins: tuple[str, ...]
    celery_broker_url: str | None
    celery_result_backend: str | None
    worker_enabled: bool
    vector_backend: str
    vector_collection_name: str
    chroma_persist_directory: Path
    embedding_model_name: str
    max_upload_size_mb: int


def load_settings() -> Settings:
    project_root = Path(__file__).resolve().parents[2]
    environment = os.getenv("EDUTRACK_ENVIRONMENT", "development").strip().lower()
    debug = _as_bool(os.getenv("EDUTRACK_DEBUG"), default=False)
    api_version = os.getenv("EDUTRACK_API_VERSION", "v1").strip()

    default_database_url = (
        "postgresql://edutrack:password@localhost:5432/edutrack_db"
        if environment in {"staging", "production"}
        else "sqlite:///./edutrack.db"
    )

    raw_origins = os.getenv(
        "EDUTRACK_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://localhost:8080",
    )
    cors_origins = tuple(origin.strip() for origin in raw_origins.split(",") if origin.strip())

    return Settings(
        project_name="EduTrack",
        api_version=api_version,
        environment=environment,
        debug=debug,
        project_root=project_root,
        api_prefix=f"/api/{api_version}",
        database_url=os.getenv("DATABASE_URL", default_database_url),
        secret_key=os.getenv("SECRET_KEY", secrets.token_urlsafe(32)),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
        cors_origins=cors_origins,
        celery_broker_url=os.getenv("CELERY_BROKER_URL"),
        celery_result_backend=os.getenv("CELERY_RESULT_BACKEND"),
        worker_enabled=_as_bool(os.getenv("EDUTRACK_WORKER_ENABLED"), default=False),
        vector_backend=os.getenv("VECTOR_BACKEND", "chroma").strip().lower(),
        vector_collection_name=os.getenv("VECTOR_COLLECTION_NAME", "edutrack_documents").strip(),
        chroma_persist_directory=project_root / os.getenv("CHROMA_PERSIST_DIRECTORY", "data/chroma"),
        embedding_model_name=os.getenv(
            "EMBEDDING_MODEL_NAME",
            "sentence-transformers/all-MiniLM-L6-v2",
        ).strip(),
        max_upload_size_mb=int(os.getenv("MAX_UPLOAD_SIZE_MB", "25")),
    )


settings = load_settings()
