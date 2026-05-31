import secrets

import pyotp
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationError
from app.models.two_factor import TwoFactorSecret


def generate_secret(user_id: str) -> dict:
    """Generate a new TOTP secret for a user.

    Returns dict with 'secret' (base32 string) and 'qr_code_url' (otpauth URI).
    """
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    otpauth_uri = totp.provisioning_uri(
        name=user_id,
        issuer_name="FinHub",
    )
    return {
        "secret": secret,
        "qr_code_url": otpauth_uri,
    }


def verify_code(secret: str, code: str) -> bool:
    """Validate a TOTP code with a 30-second window.

    Returns True if the code is valid.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)


def enable_2fa(session: Session, user_id: str, code: str) -> bool:
    """Verify the code, then enable 2FA for the user.

    Returns True if 2FA was enabled successfully.
    """
    record = session.query(TwoFactorSecret).filter(
        TwoFactorSecret.user_id == user_id
    ).first()

    if record is None:
        raise ValidationError("No 2FA secret found. Generate one first.")

    if not verify_code(record.secret, code):
        raise ValidationError("Invalid verification code")

    record.is_enabled = True
    session.commit()
    return True


def disable_2fa(session: Session, user_id: str) -> None:
    """Disable and remove 2FA for the user."""
    session.query(TwoFactorSecret).filter(
        TwoFactorSecret.user_id == user_id
    ).delete(synchronize_session="fetch")
    session.commit()
