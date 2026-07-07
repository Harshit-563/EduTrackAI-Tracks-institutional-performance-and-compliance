from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRole(str, Enum):
    INSTITUTION = "institution"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class DocumentStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    PARSED = "parsed"
    NEEDS_MANUAL_REVIEW = "needs_manual_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    LOW_CONFIDENCE = "low_confidence"
    FAILED = "failed"


class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"


class ReportType(str, Enum):
    DOCUMENT = "document"
    INSTITUTION = "institution"
    COMPLIANCE = "compliance"


class PredictionType(str, Enum):
    COMPLIANCE = "compliance"
    RISK = "risk"
    PERFORMANCE = "performance"
    ANOMALY = "anomaly"
    CLASSIFICATION = "classification"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        Index("idx_users_email", "email"),
        Index("idx_users_role", "role"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole, native_enum=False), nullable=False)
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institutions.id", ondelete="SET NULL"))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    institution: Mapped["Institution | None"] = relationship(back_populates="users")
    documents: Mapped[list["Document"]] = relationship(back_populates="uploaded_by_user")
    review_actions: Mapped[list["ReviewAction"]] = relationship(back_populates="reviewer")
    auth_tokens: Mapped[list["AuthToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="user")


class Institution(Base):
    __tablename__ = "institutions"
    __table_args__ = (
        UniqueConstraint("name", name="uq_institutions_name"),
        Index("idx_institutions_name", "name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    total_students: Mapped[int | None] = mapped_column(Integer)
    total_faculty: Mapped[int | None] = mapped_column(Integer)
    placement_rate: Mapped[float | None] = mapped_column(Float)
    fund_utilization: Mapped[float | None] = mapped_column(Float)
    infrastructure_area: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    users: Mapped[list[User]] = relationship(back_populates="institution")
    documents: Mapped[list["Document"]] = relationship(back_populates="institution", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="institution")
    compliance_rules: Mapped[list["ComplianceRule"]] = relationship(back_populates="institution")


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        UniqueConstraint("submission_code", name="uq_documents_submission_code"),
        Index("idx_documents_institution_id", "institution_id"),
        Index("idx_documents_status", "status"),
        Index("idx_documents_type", "doc_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_code: Mapped[str] = mapped_column(String(50), nullable=False)
    institution_id: Mapped[int] = mapped_column(ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(100), default="unknown", nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(255))
    storage_path: Mapped[str | None] = mapped_column(String(500))
    mime_type: Mapped[str | None] = mapped_column(String(100))
    content_hash: Mapped[str | None] = mapped_column(String(128))
    ocr_text: Mapped[str | None] = mapped_column(Text)
    dss_score: Mapped[float | None] = mapped_column(Float)
    compliance_score: Mapped[float | None] = mapped_column(Float)
    status: Mapped[DocumentStatus] = mapped_column(
        SqlEnum(DocumentStatus, native_enum=False),
        default=DocumentStatus.QUEUED,
        nullable=False,
    )
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime)
    flags: Mapped[list[str]] = mapped_column(MutableList.as_mutable(JSON), default=list, nullable=False)
    extracted_fields: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSON),
        default=dict,
        nullable=False,
    )
    classification_label: Mapped[str | None] = mapped_column(String(100))
    classification_confidence: Mapped[float | None] = mapped_column(Float)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    institution: Mapped[Institution] = relationship(back_populates="documents")
    uploaded_by_user: Mapped[User | None] = relationship(back_populates="documents")
    review_actions: Mapped[list["ReviewAction"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    predictions: Mapped[list["AIPrediction"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="document", cascade="all, delete-orphan")


Submission = Document


class ReviewAction(Base):
    __tablename__ = "review_actions"
    __table_args__ = (
        Index("idx_review_actions_document_id", "document_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    document: Mapped[Document] = relationship(back_populates="review_actions")
    reviewer: Mapped[User] = relationship(back_populates="review_actions")


class AuthToken(Base):
    __tablename__ = "auth_tokens"
    __table_args__ = (
        UniqueConstraint("token_hash", name="uq_auth_tokens_hash"),
        Index("idx_auth_tokens_user_id", "user_id"),
        Index("idx_auth_tokens_expires_at", "expires_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_type: Mapped[str] = mapped_column(String(20), default="refresh", nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="auth_tokens")


class ComplianceRule(Base):
    __tablename__ = "compliance_rules"
    __table_args__ = (
        UniqueConstraint("rule_code", name="uq_compliance_rules_code"),
        Index("idx_compliance_rules_doc_type", "doc_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_code: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    doc_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="medium", nullable=False)
    required_keywords: Mapped[list[str]] = mapped_column(MutableList.as_mutable(JSON), default=list, nullable=False)
    rule_definition: Mapped[dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institutions.id", ondelete="SET NULL"))
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    institution: Mapped[Institution | None] = relationship(back_populates="compliance_rules")


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        Index("idx_reports_document_id", "document_id"),
        Index("idx_reports_institution_id", "institution_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    report_type: Mapped[ReportType] = mapped_column(SqlEnum(ReportType, native_enum=False), nullable=False)
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"))
    institution_id: Mapped[int | None] = mapped_column(ForeignKey("institutions.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    document: Mapped[Document | None] = relationship(back_populates="reports")
    institution: Mapped[Institution | None] = relationship(back_populates="reports")


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("idx_notifications_user_id", "user_id"),
        Index("idx_notifications_status", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        SqlEnum(NotificationStatus, native_enum=False),
        default=NotificationStatus.UNREAD,
        nullable=False,
    )
    metadata_json: Mapped[dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="notifications")


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_logs_document_id", "document_id"),
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_action", "action"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    document_id: Mapped[int | None] = mapped_column(ForeignKey("documents.id", ondelete="SET NULL"))
    payload: Mapped[dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User | None] = relationship(back_populates="audit_logs")
    document: Mapped[Document | None] = relationship(back_populates="audit_logs")


class AIPrediction(Base):
    __tablename__ = "ai_predictions"
    __table_args__ = (
        Index("idx_ai_predictions_document_id", "document_id"),
        Index("idx_ai_predictions_prediction_type", "prediction_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    prediction_type: Mapped[PredictionType] = mapped_column(
        SqlEnum(PredictionType, native_enum=False),
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[float | None] = mapped_column(Float)
    label: Mapped[str | None] = mapped_column(String(255))
    confidence: Mapped[float | None] = mapped_column(Float)
    explanation: Mapped[dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(MutableDict.as_mutable(JSON), default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    document: Mapped[Document] = relationship(back_populates="predictions")
