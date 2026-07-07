from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.auth.utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
    verify_password,
    verify_token_hash,
)
from src.core.config import settings
from src.database.repositories import AuthTokenRepository, UserRepository


class AuthService:
    def authenticate(self, email: str, password: str, db: Session) -> dict[str, str | int]:
        user = UserRepository(db).get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
        return {
            "email": user.email,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "user_id": user.id,
            "institution_id": user.institution_id,
        }

    def issue_tokens(self, user_id: int, email: str, role: str, db: Session) -> dict[str, str | int]:
        access_token = create_access_token(
            data={"sub": email, "user_id": user_id, "role": role},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )
        refresh_token = create_refresh_token(data={"sub": email, "user_id": user_id, "role": role})

        repo = AuthTokenRepository(db)
        expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        repo.create(
            token_hash=hash_token(refresh_token),
            user_id=user_id,
            expires_at=expires_at,
            token_type="refresh",
        )
        db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        }

    def get_current_user(self, token: str, db: Session) -> dict[str, str | int]:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

        user_id = payload.get("user_id")
        user = UserRepository(db).get(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

        return {
            "email": user.email,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
            "user_id": user.id,
            "institution_id": user.institution_id,
        }

    def refresh_access_token(self, refresh_token: str, db: Session) -> dict[str, str | int]:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user_id = payload.get("user_id")
        email = payload.get("sub")
        role = payload.get("role")
        if not user_id or not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

        repo = AuthTokenRepository(db)
        active_tokens = repo.get_active_tokens_for_user(user_id)
        if not any(verify_token_hash(refresh_token, item.token_hash) for item in active_tokens):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked or unknown")

        user = UserRepository(db).get(user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

        access_token = create_access_token(
            data={"sub": email, "user_id": user_id, "role": role or user.role.value},
            expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        }
