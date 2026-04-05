from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Account
from app.schemas.accounts import AccountResponse

router = APIRouter()


@router.get("/accounts", response_model=list[AccountResponse])
def list_accounts(db: Session = Depends(get_db)) -> list[AccountResponse]:
    return db.query(Account).order_by(Account.name.asc()).all()
