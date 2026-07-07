from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, Iterable, Optional, TypeVar

from sqlalchemy.orm import Session

from src.database.models import (
    AIPrediction,
    AuditLog,
    AuthToken,
    ComplianceRule,
    Document,
    DocumentStatus,
    Institution,
    Notification,
    Report,
    ReviewAction,
    User,
)


ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    def __init__(self, db: Session, model: type[ModelT]):
        self.db = db
        self.model = model

    def add(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        self.db.flush()
        return instance

    def get(self, entity_id: int) -> ModelT | None:
        return self.db.get(self.model, entity_id)

    def list_all(self) -> list[ModelT]:
        return self.db.query(self.model).all()


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.get(user_id)

    def create(self, email: str, password_hash: str, role: str, institution_id: int | None = None) -> User:
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            role=role,
            institution_id=institution_id,
        )
        return self.add(user)


class InstitutionRepository(BaseRepository[Institution]):
    def __init__(self, db: Session):
        super().__init__(db, Institution)

    def get_by_name(self, name: str) -> Institution | None:
        return self.db.query(Institution).filter(Institution.name == name).first()

    def get_by_id(self, institution_id: int) -> Institution | None:
        return self.get(institution_id)

    def create(self, name: str, **kwargs: Any) -> Institution:
        institution = Institution(name=name, **kwargs)
        return self.add(institution)


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, db: Session):
        super().__init__(db, Document)

    def get_by_code(self, submission_code: str) -> Document | None:
        return self.db.query(Document).filter(Document.submission_code == submission_code).first()

    def get_by_id(self, document_id: int) -> Document | None:
        return self.get(document_id)

    def get_by_institution(self, institution_id: int, limit: int = 100, offset: int = 0) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(Document.institution_id == institution_id)
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_by_institution(self, institution_id: int) -> int:
        return self.db.query(Document).filter(Document.institution_id == institution_id).count()

    def get_processing_queue(self, limit: int = 50, offset: int = 0) -> list[Document]:
        return (
            self.db.query(Document)
            .filter(Document.status.in_([DocumentStatus.QUEUED, DocumentStatus.PROCESSING, DocumentStatus.NEEDS_MANUAL_REVIEW]))
            .order_by(Document.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, **kwargs: Any) -> Document:
        document = Document(**kwargs)
        return self.add(document)

    def update_status(self, document: Document, status: DocumentStatus, *, flags: list[str] | None = None) -> Document:
        document.status = status
        document.updated_at = datetime.utcnow()
        if flags is not None:
            document.flags = flags
        self.db.flush()
        return document


class SubmissionRepository(DocumentRepository):
    pass


class ReviewActionRepository(BaseRepository[ReviewAction]):
    def __init__(self, db: Session):
        super().__init__(db, ReviewAction)

    def get_by_document(self, document_id: int) -> list[ReviewAction]:
        return self.db.query(ReviewAction).filter(ReviewAction.document_id == document_id).all()

    def get_by_submission(self, submission_id: int) -> list[ReviewAction]:
        return self.get_by_document(submission_id)

    def create(self, document_id: int, reviewer_id: int, action: str, notes: str | None = None) -> ReviewAction:
        review = ReviewAction(
            document_id=document_id,
            reviewer_id=reviewer_id,
            action=action,
            notes=notes,
        )
        return self.add(review)


class AuthTokenRepository(BaseRepository[AuthToken]):
    def __init__(self, db: Session):
        super().__init__(db, AuthToken)

    def get_active_tokens_for_user(self, user_id: int) -> list[AuthToken]:
        now = datetime.utcnow()
        return (
            self.db.query(AuthToken)
            .filter(AuthToken.user_id == user_id, AuthToken.expires_at >= now, AuthToken.revoked_at.is_(None))
            .all()
        )

    def get_by_hash(self, token_hash: str) -> AuthToken | None:
        return self.db.query(AuthToken).filter(AuthToken.token_hash == token_hash).first()

    def create(self, token_hash: str, user_id: int, expires_at: datetime, token_type: str = "refresh") -> AuthToken:
        token = AuthToken(
            token_hash=token_hash,
            user_id=user_id,
            expires_at=expires_at,
            token_type=token_type,
        )
        return self.add(token)

    def revoke_token(self, token: AuthToken) -> AuthToken:
        token.revoked_at = datetime.utcnow()
        self.db.flush()
        return token

    def revoke_all_for_user(self, user_id: int, token_type: str = "refresh") -> int:
        tokens = (
            self.db.query(AuthToken)
            .filter(AuthToken.user_id == user_id, AuthToken.token_type == token_type, AuthToken.revoked_at.is_(None))
            .all()
        )
        for token in tokens:
            token.revoked_at = datetime.utcnow()
        self.db.flush()
        return len(tokens)

    def delete_expired(self) -> int:
        count = self.db.query(AuthToken).filter(AuthToken.expires_at < datetime.utcnow()).delete()
        self.db.flush()
        return count


class ComplianceRuleRepository(BaseRepository[ComplianceRule]):
    def __init__(self, db: Session):
        super().__init__(db, ComplianceRule)

    def list_for_doc_type(self, doc_type: str) -> list[ComplianceRule]:
        return (
            self.db.query(ComplianceRule)
            .filter(ComplianceRule.doc_type == doc_type, ComplianceRule.is_active.is_(True))
            .all()
        )


class ReportRepository(BaseRepository[Report]):
    def __init__(self, db: Session):
        super().__init__(db, Report)

    def create(self, **kwargs: Any) -> Report:
        return self.add(Report(**kwargs))


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: Session):
        super().__init__(db, Notification)

    def create(self, **kwargs: Any) -> Notification:
        return self.add(Notification(**kwargs))


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: Session):
        super().__init__(db, AuditLog)

    def create(self, **kwargs: Any) -> AuditLog:
        return self.add(AuditLog(**kwargs))


class AIPredictionRepository(BaseRepository[AIPrediction]):
    def __init__(self, db: Session):
        super().__init__(db, AIPrediction)

    def create(self, **kwargs: Any) -> AIPrediction:
        return self.add(AIPrediction(**kwargs))
