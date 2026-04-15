from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from fastapi import Cookie, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.security import hash_session_token, session_expiry
from app.db.session import get_db
from app.models.auth import AuthSession, User


SLIDING_REFRESH_THRESHOLD_DAYS = 7


class UnauthorizedError(AppError):
    status_code = 401
    error_code = "unauthorized"

    def __init__(self, detail: str = "Authentication required"):
        super().__init__(detail)


@dataclass
class AuthContext:
    user: User
    session: AuthSession


def _load_session(db: Session, session_token: str | None) -> AuthSession | None:
    if not session_token:
        return None
    now = datetime.now(UTC)
    return db.scalar(
        select(AuthSession)
        .options(selectinload(AuthSession.user))
        .where(
            AuthSession.token_hash == hash_session_token(session_token),
            AuthSession.expires_at > now,
        )
    )


def get_auth_context(
    db: Session = Depends(get_db),
    session_token: str | None = Cookie(default=None, alias=settings.auth_session_cookie),
) -> AuthContext:
    session = _load_session(db, session_token)
    if not session or not session.user or not session.user.is_active:
        raise UnauthorizedError()

    now = datetime.now(UTC)
    session.last_seen_at = now
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at - now < timedelta(days=SLIDING_REFRESH_THRESHOLD_DAYS):
        session.expires_at = session_expiry()
    db.commit()
    db.refresh(session)
    return AuthContext(user=session.user, session=session)


def get_current_user(ctx: AuthContext = Depends(get_auth_context)) -> User:
    return ctx.user


def require_auth(user: User = Depends(get_current_user)) -> User:
    return user


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    return request.client.host if request.client else None


def session_metadata(request: Request) -> dict:
    ua = request.headers.get("user-agent")
    return {
        "user_agent": (ua or None) and ua[:500],
        "ip_address": _client_ip(request),
    }
