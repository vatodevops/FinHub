from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.db.session import get_db
from app.models.auth import User
from app.models.entities import Institution
from app.schemas.institutions import InstitutionResponse

router = APIRouter()


@router.get("/institutions", response_model=list[InstitutionResponse])
def list_institutions(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[InstitutionResponse]:
    return (
        db.query(Institution)
        .filter(Institution.user_id == user.id)
        .order_by(Institution.name.asc())
        .all()
    )
