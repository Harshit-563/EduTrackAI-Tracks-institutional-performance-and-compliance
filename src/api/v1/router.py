from fastapi import APIRouter

from .routes.health import router as health_router
from .routes.auth import router as auth_router
from .routes.reviewer import router as reviewer_router
from .routes.upload import router as upload_router
from .routes.institutions import router as institutions_router
from .routes.documents import router as documents_router
from .routes.predictions import router as predictions_router

router = APIRouter()
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(reviewer_router)
router.include_router(upload_router)
router.include_router(institutions_router)
router.include_router(documents_router)
router.include_router(predictions_router)
