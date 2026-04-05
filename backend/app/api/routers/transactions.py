import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.entities import Transaction
from app.schemas.categories import TransactionCategoryUpdate
from app.schemas.duplicates import CurveDuplicateCandidateResponse
from app.schemas.transactions import TransactionResponse, tx_payload
from app.services.duplicates import list_curve_duplicate_candidates

router = APIRouter()


@router.get("/transactions", response_model=list[TransactionResponse])
def list_transactions(
    account_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[TransactionResponse]:
    query = db.query(Transaction)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    rows = query.order_by(Transaction.booked_at.desc().nullslast(), Transaction.created_at.desc()).limit(limit).all()
    return [TransactionResponse.model_validate(tx_payload(tx)) for tx in rows]


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    from app.models.categories import Category
    from app.schemas.categories import CategoryResponse

    return db.query(Category).order_by(Category.name.asc()).all()


@router.patch("/transactions/{transaction_id}/category", response_model=TransactionResponse)
def update_transaction_category(
    transaction_id: uuid.UUID,
    payload: TransactionCategoryUpdate,
    db: Session = Depends(get_db),
) -> TransactionResponse:
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).one_or_none()
    if tx is None:
        raise NotFoundError("transaction_not_found")
    tx.category_id = payload.category_id
    db.commit()
    db.refresh(tx)
    return TransactionResponse.model_validate(tx_payload(tx))


@router.get("/transactions/curve-duplicates", response_model=list[CurveDuplicateCandidateResponse])
def curve_duplicates(db: Session = Depends(get_db)) -> list[CurveDuplicateCandidateResponse]:
    return list_curve_duplicate_candidates(db)
