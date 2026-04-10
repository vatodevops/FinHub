from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Response
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.api.deps.auth import get_current_user
from app.core.config import settings
from app.core.exceptions import ConflictError, ValidationError
from app.core.security import generate_session_token, hash_password, hash_session_token, session_expiry, verify_password
from app.db.session import get_db
from app.models.auth import AuthSession, User
from app.schemas.auth import LoginRequest, RegisterRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.auth_session_cookie,
        value=token,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=settings.auth_session_days * 24 * 60 * 60,
        path="/",
    )


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> UserResponse:
    existing = db.scalar(select(User).where(func.lower(User.email) == payload.email.lower()))
    if existing:
        raise ConflictError("Ya existe una cuenta con ese email")

    user = User(email=payload.email.lower(), full_name=(payload.full_name or None), password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()

    token = generate_session_token()
    db.add(AuthSession(user_id=user.id, token_hash=hash_session_token(token), expires_at=session_expiry(), last_seen_at=datetime.now(UTC)))
    db.commit()
    db.refresh(user)
    _set_session_cookie(response, token)
    return user


@router.post("/login", response_model=UserResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> UserResponse:
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise ValidationError("Credenciales invalidas")
    if not user.is_active:
        raise ValidationError("La cuenta esta desactivada")

    token = generate_session_token()
    db.add(AuthSession(user_id=user.id, token_hash=hash_session_token(token), expires_at=session_expiry(), last_seen_at=datetime.now(UTC)))
    db.commit()
    _set_session_cookie(response, token)
    return user


@router.post("/logout", status_code=204)
def logout(
    response: Response,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.execute(delete(AuthSession).where(AuthSession.user_id == current_user.id))
    db.commit()
    response.delete_cookie(key=settings.auth_session_cookie, path="/", samesite="lax")
    return response


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user
