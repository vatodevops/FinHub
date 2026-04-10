from datetime import UTC, datetime

from fastapi import Cookie, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import hash_session_token
from app.db.session import get_db
from app.models.auth import AuthSession, User


class UnauthorizedError(AppError):
    status_code = 401
    error_code = "unauthorized"

    def __init__(self, detail: str = "Authentication required"):
        super().__init__(detail)



def get_current_user(
    db: Session = Depends(get_db),
    session_token: str | None = Cookie(default=None, alias=settings.auth_session_cookie),
) -> User:
    if not session_token:
        raise UnauthorizedError()

    now = datetime.now(UTC)
    session = db.scalar(
        select(AuthSession)
        .options(selectinload(AuthSession.user))
        .where(AuthSession.token_hash == hash_session_token(session_token), AuthSession.expires_at > now)
    )
    if not session or not session.user or not session.user.is_active:
        raise UnauthorizedError()

    session.last_seen_at = now
    db.commit()
    db.refresh(session)
    return session.user



def require_auth(user: User = Depends(get_current_user)) -> User:
    return user
