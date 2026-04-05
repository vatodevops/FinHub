from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Institution
from app.schemas.institutions import InstitutionResponse

router = APIRouter()


@router.get("/institutions", response_model=list[InstitutionResponse])
def list_institutions(db: Session = Depends(get_db)) -> list[InstitutionResponse]:
    return db.query(Institution).order_by(Institution.name.asc()).all()
