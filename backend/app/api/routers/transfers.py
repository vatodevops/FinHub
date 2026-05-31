from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.db.session import get_db
from app.models.auth import User
from app.services.transfer_detection import detect_transfer_pairs

router = APIRouter(tags=["transfers"])


@router.post("/detect", response_model=dict)
def detect_transfers(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> dict:
    """Manually trigger transfer detection for the current user.

    Scans unpaired transactions and creates transfer_pair links
    for matching debit/credit pairs.
    """
    pairs = detect_transfer_pairs(db, user.id)
    return {"pairs_created": pairs}
