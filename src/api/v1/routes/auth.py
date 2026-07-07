from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.v1.schemas import LoginPayload, RefreshTokenPayload, TokenResponse, UserResponse
from src.auth.dependencies import get_current_user
from src.database import get_db
from src.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Auth"])
auth_service = AuthService()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginPayload, db: Session = Depends(get_db)) -> dict:
    user = auth_service.authenticate(payload.email, payload.password, db)
    tokens = auth_service.issue_tokens(user["user_id"], user["email"], user["role"], db)
    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "token_type": tokens["token_type"],
        "expires_in": tokens["expires_in"],
        "user": {
            "email": user["email"],
            "role": user["role"],
            "institution_id": user.get("institution_id"),
        },
    }


@router.post("/refresh")
def refresh_token(payload: RefreshTokenPayload, db: Session = Depends(get_db)) -> dict:
    return auth_service.refresh_access_token(payload.refresh_token, db)


@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)) -> dict:
    return {
        "email": user["email"],
        "role": user["role"],
        "institution_id": user.get("institution_id"),
    }
