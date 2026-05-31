import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.core.exceptions import ValidationError
from app.db.session import get_db
from app.models.auth import User
from app.models.two_factor import TwoFactorSecret
from app.schemas.two_factor import TwoFactorSetupResponse, TwoFactorVerifyRequest

router = APIRouter(prefix="/auth/2fa", tags=["2fa"])


@router.post("/setup", response_model=TwoFactorSetupResponse)
def setup_2fa(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> TwoFactorSetupResponse:
    """Generate a new 2FA secret for the user."""
    from app.services.two_factor_service import generate_secret

    result = generate_secret(user.id)

    # Store the secret (disabled until verified)
    existing = db.query(TwoFactorSecret).filter(
        TwoFactorSecret.user_id == user.id
    ).first()

    if existing:
        existing.secret = result["secret"]
        existing.is_enabled = False
    else:
        db.add(
            TwoFactorSecret(
                user_id=user.id,
                secret=result["secret"],
                is_enabled=False,
            )
        )

    db.commit()

    return TwoFactorSetupResponse(
        qr_code_url=result["qr_code_url"],
        secret=result["secret"],
    )


@router.post("/verify")
def verify_2fa(
    payload: TwoFactorVerifyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> dict:
    """Verify the TOTP code and enable 2FA."""
    from app.services.two_factor_service import enable_2fa

    enable_2fa(db, user.id, payload.code)
    return {"enabled": True}


@router.post("/disable")
def disable_2fa(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> dict:
    """Disable 2FA for the user."""
    from app.services.two_factor_service import disable_2fa

    disable_2fa(db, user.id)
    return {"disabled": True}
