import uuid
from datetime import UTC, datetime
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.api.deps.auth import AuthContext, get_auth_context, get_current_user, session_metadata
from app.core.config import settings
from app.core.exceptions import ConflictError, ValidationError
from app.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    session_expiry,
    verify_password,
)
from app.db.seed import seed_default_categories
from app.db.session import get_db
from app.models.auth import AuthSession, User
from app.schemas.auth import AuthSessionResponse, LoginRequest, RegisterRequest, UserResponse

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


def _delete_session_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.auth_session_cookie,
        path="/",
        samesite="lax",
        secure=settings.environment == "production",
    )


def _delete_oauth_state_cookie(response: Response) -> None:
    response.delete_cookie(
        key=settings.oauth_state_cookie,
        path="/",
        samesite="lax",
        secure=settings.environment == "production",
    )


def _frontend_login_url(error: str | None = None) -> str:
    base = f"{settings.frontend_base_url.rstrip('/')}/login"
    if not error:
        return base
    return f"{base}?{urlencode({'error': error})}"


def _issue_session(db: Session, user: User, request: Request, now: datetime) -> str:
    meta = session_metadata(request)
    token = generate_session_token()
    db.add(
        AuthSession(
            user_id=user.id,
            token_hash=hash_session_token(token),
            expires_at=session_expiry(),
            last_seen_at=now,
            user_agent=meta["user_agent"],
            ip_address=meta["ip_address"],
        )
    )
    return token


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    payload: RegisterRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> UserResponse:
    existing = db.scalar(select(User).where(func.lower(User.email) == payload.email.lower()))
    if existing:
        raise ConflictError("Ya existe una cuenta con ese email")

    now = datetime.now(UTC)
    user = User(
        email=payload.email.lower(),
        full_name=(payload.full_name or None),
        password_hash=hash_password(payload.password),
        auth_provider="local",
        last_login_at=now,
    )
    db.add(user)
    db.flush()
    seed_default_categories(db, user.id)

    token = _issue_session(db, user, request, now)
    db.commit()
    db.refresh(user)
    _set_session_cookie(response, token)
    return user


@router.post("/login", response_model=UserResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> UserResponse:
    user = db.scalar(select(User).where(func.lower(User.email) == payload.email.lower()))
    if not user:
        raise ValidationError("Credenciales invalidas")
    if not user.password_hash or user.auth_provider != "local":
        raise ValidationError("Esta cuenta se identifica con Google. Entra con Google.")
    if not verify_password(payload.password, user.password_hash):
        raise ValidationError("Credenciales invalidas")
    if not user.is_active:
        raise ValidationError("La cuenta esta desactivada")

    now = datetime.now(UTC)
    user.last_login_at = now
    token = _issue_session(db, user, request, now)
    db.commit()
    _set_session_cookie(response, token)
    return user


@router.post("/logout")
def logout(
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
):
    db.execute(delete(AuthSession).where(AuthSession.id == ctx.session.id))
    db.commit()
    json_response = JSONResponse({"ok": True})
    _delete_session_cookie(json_response)
    return json_response


@router.post("/logout-all")
def logout_all(
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
):
    db.execute(delete(AuthSession).where(AuthSession.user_id == ctx.user.id))
    db.commit()
    json_response = JSONResponse({"ok": True})
    _delete_session_cookie(json_response)
    return json_response


@router.get("/sessions", response_model=list[AuthSessionResponse])
def list_sessions(
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
) -> list[AuthSessionResponse]:
    rows = db.scalars(
        select(AuthSession)
        .where(AuthSession.user_id == ctx.user.id)
        .order_by(AuthSession.last_seen_at.desc().nullslast(), AuthSession.created_at.desc())
    ).all()
    return [
        AuthSessionResponse(
            id=row.id,
            created_at=row.created_at,
            expires_at=row.expires_at,
            last_seen_at=row.last_seen_at,
            user_agent=row.user_agent,
            ip_address=row.ip_address,
            current=row.id == ctx.session.id,
        )
        for row in rows
    ]


@router.delete("/sessions/{session_id}", status_code=204)
def revoke_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    ctx: AuthContext = Depends(get_auth_context),
):
    db.execute(
        delete(AuthSession).where(
            AuthSession.id == session_id,
            AuthSession.user_id == ctx.user.id,
        )
    )
    db.commit()


@router.get("/google/start")
def google_start():
    if not settings.google_client_id or not settings.google_client_secret:
        return RedirectResponse(_frontend_login_url("google_oauth_no_configurado"), status_code=302)

    state = generate_session_token()
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    response = RedirectResponse(
        "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params),
        status_code=302,
    )
    response.set_cookie(
        key=settings.oauth_state_cookie,
        value=state,
        httponly=True,
        secure=settings.environment == "production",
        samesite="lax",
        max_age=10 * 60,
        path="/",
    )
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    cookie_state = request.cookies.get(settings.oauth_state_cookie)
    if not code or not state or not cookie_state or state != cookie_state:
        response = RedirectResponse(_frontend_login_url("google_oauth_state_invalido"), status_code=302)
        _delete_oauth_state_cookie(response)
        return response

    if not settings.google_client_id or not settings.google_client_secret:
        response = RedirectResponse(_frontend_login_url("google_oauth_no_configurado"), status_code=302)
        _delete_oauth_state_cookie(response)
        return response

    async with httpx.AsyncClient(timeout=20) as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_res.status_code >= 400:
            response = RedirectResponse(_frontend_login_url("google_oauth_token_error"), status_code=302)
            _delete_oauth_state_cookie(response)
            return response

        token_data = token_res.json()
        access_token = token_data.get("access_token")
        if not access_token:
            response = RedirectResponse(_frontend_login_url("google_oauth_token_error"), status_code=302)
            _delete_oauth_state_cookie(response)
            return response

        userinfo_res = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if userinfo_res.status_code >= 400:
            response = RedirectResponse(_frontend_login_url("google_oauth_userinfo_error"), status_code=302)
            _delete_oauth_state_cookie(response)
            return response

    profile = userinfo_res.json()
    email = (profile.get("email") or "").lower().strip()
    google_sub = profile.get("sub")
    full_name = profile.get("name")
    picture = profile.get("picture")
    locale = profile.get("locale")
    email_verified = bool(profile.get("email_verified"))

    if not email or not google_sub or not email_verified:
        response = RedirectResponse(_frontend_login_url("google_oauth_email_no_valido"), status_code=302)
        _delete_oauth_state_cookie(response)
        return response

    user = db.scalar(select(User).where(User.google_sub == google_sub))
    if not user:
        user = db.scalar(select(User).where(func.lower(User.email) == email))

    now = datetime.now(UTC)
    if user:
        if user.google_sub and user.google_sub != google_sub:
            response = RedirectResponse(_frontend_login_url("google_oauth_conflicto"), status_code=302)
            _delete_oauth_state_cookie(response)
            return response
        user.google_sub = google_sub
        user.email_verified = True
        if full_name:
            user.full_name = full_name
        if picture:
            user.picture_url = picture
        if locale:
            user.locale = locale
        if user.auth_provider == "local" and not user.password_hash:
            user.auth_provider = "google"
        elif user.auth_provider != "local":
            user.auth_provider = "google"
        user.last_login_at = now
    else:
        user = User(
            email=email,
            full_name=full_name,
            picture_url=picture,
            locale=locale,
            email_verified=True,
            password_hash=None,
            auth_provider="google",
            google_sub=google_sub,
            last_login_at=now,
        )
        db.add(user)
        db.flush()
        seed_default_categories(db, user.id)

    token = _issue_session(db, user, request, now)
    db.commit()

    response = RedirectResponse(settings.frontend_base_url.rstrip("/") + "/", status_code=302)
    _delete_oauth_state_cookie(response)
    _set_session_cookie(response, token)
    return response


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user
