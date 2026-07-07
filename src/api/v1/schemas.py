from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LoginPayload(BaseModel):
    email: str = Field(..., min_length=5, description="User email address")
    password: str = Field(..., min_length=6, description="User password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Invalid email format")
        return value.lower()


class RefreshTokenPayload(BaseModel):
    refresh_token: str = Field(..., min_length=20, description="Refresh token for obtaining new access token")


class ReviewActionPayload(BaseModel):
    action: str = Field(..., description="Action: approved, rejected, needs_manual_review")
    notes: str | None = Field(None, max_length=1000, description="Reviewer notes")

    @field_validator("action")
    @classmethod
    def validate_action(cls, value: str) -> str:
        allowed = {"approved", "rejected", "needs_manual_review"}
        if value not in allowed:
            raise ValueError(f"Action must be one of: {sorted(allowed)}")
        return value


class UserResponse(BaseModel):
    email: str
    role: str
    institution_id: int | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class DocumentSearchResponse(BaseModel):
    submission_code: str
    doc_type: str
    score: float
    excerpt: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)
