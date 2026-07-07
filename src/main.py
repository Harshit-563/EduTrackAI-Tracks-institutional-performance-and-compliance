from __future__ import annotations

from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1.router import router as api_v1_router
from src.core.config import settings
from src.core.exceptions import register_exception_handlers
from src.core.logging import configure_logging, get_logger
from src.database import init_db


load_dotenv()
configure_logging()
logger = get_logger(__name__)

app = FastAPI(
    title=f"{settings.project_name} Backend API",
    description="AI-Based Institutional Compliance, Document Review, and Risk System",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

register_exception_handlers(app)


@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("EduTrack backend started in %s mode", settings.environment)


app.include_router(api_v1_router, prefix=settings.api_prefix)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": settings.project_name,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
    }
