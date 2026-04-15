from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.db.session import get_db
from app.models.auth import User
from app.schemas.overview import OverviewResponse
from app.services.overview import build_overview

router = APIRouter()


@router.get("/overview", response_model=OverviewResponse)
def overview(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> OverviewResponse:
    return build_overview(db, user.id)
