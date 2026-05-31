import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.core.exceptions import NotFoundError, ValidationError
from app.db.session import get_db
from app.models.auth import User
from app.models.entities import Transaction
from app.models.transaction_split import TransactionSplit
from app.schemas.transactions import TransactionResponse, tx_payload

router = APIRouter(tags=["transaction-splits"])


@router.get(
    "/transactions/{transaction_id}/splits",
    response_model=list[dict],
)
def list_splits(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[dict]:
    """List all splits for a transaction."""
    tx = db.scalar(
        select(Transaction)
        .where(Transaction.id == transaction_id, Transaction.user_id == user.id)
    )
    if tx is None:
        raise NotFoundError("Transaction not found")

    splits = db.query(TransactionSplit).filter(
        TransactionSplit.transaction_id == transaction_id
    ).order_by(TransactionSplit.created_at).all()

    return [
        {
            "id": str(s.id),
            "transaction_id": str(s.transaction_id),
            "category_id": str(s.category_id) if s.category_id else None,
            "amount": float(s.amount),
            "description": s.description,
            "notes": s.notes,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in splits
    ]


@router.put(
    "/transactions/{transaction_id}/splits",
    response_model=list[dict],
)
def replace_splits(
    transaction_id: uuid.UUID,
    splits_data: list[dict],
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[dict]:
    """Replace all splits for a transaction (whole-replacement).

    If you pass 2 splits, existing 3 get deleted and 2 new ones are created.
    The total of all split amounts must not exceed the transaction amount.
    """
    tx = db.scalar(
        select(Transaction)
        .where(Transaction.id == transaction_id, Transaction.user_id == user.id)
    )
    if tx is None:
        raise NotFoundError("Transaction not found")

    from app.services.split_service import create_splits

    result = create_splits(db, user.id, str(transaction_id), splits_data)

    return [
        {
            "id": str(s.id),
            "transaction_id": str(s.transaction_id),
            "category_id": str(s.category_id) if s.category_id else None,
            "amount": float(s.amount),
            "description": s.description,
            "notes": s.notes,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in result
    ]
