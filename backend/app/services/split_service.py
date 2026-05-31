from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import ValidationError
from app.models.entities import Transaction
from app.models.transaction_split import TransactionSplit


def create_splits(
    session: Session,
    user_id: str,
    transaction_id: str,
    splits_data: list[dict],
) -> list[TransactionSplit]:
    """Validate, delete existing splits, and create new splits for a transaction.

    The total of all split amounts must not exceed the original transaction amount.
    """
    tx = session.scalar(
        select(Transaction)
        .options(selectinload(Transaction.account))
        .where(Transaction.id == transaction_id, Transaction.user_id == user_id)
    )
    if tx is None:
        raise ValidationError("Transaction not found")

    if not splits_data:
        # Deleting all splits is allowed — just remove them
        session.query(TransactionSplit).filter(
            TransactionSplit.transaction_id == transaction_id
        ).delete(synchronize_session="fetch")
        session.commit()
        return []

    # Validate total
    total = Decimal("0")
    for item in splits_data:
        try:
            amt = Decimal(str(item["amount"]))
        except (InvalidOperation, KeyError, TypeError, ValueError):
            raise ValidationError("Invalid split amount")
        if amt < 0:
            raise ValidationError("Split amount cannot be negative")
        total += amt

    if total > tx.amount:
        raise ValidationError(
            f"Split total ({total}) exceeds transaction amount ({tx.amount})"
        )

    # Delete existing splits for this transaction
    session.query(TransactionSplit).filter(
        TransactionSplit.transaction_id == transaction_id
    ).delete(synchronize_session="fetch")

    # Create new splits
    new_splits = []
    for item in splits_data:
        split = TransactionSplit(
            user_id=user_id,
            transaction_id=transaction_id,
            category_id=item.get("category_id"),
            amount=Decimal(str(item["amount"])),
            description=item.get("description"),
            notes=item.get("notes"),
        )
        session.add(split)
        new_splits.append(split)

    session.commit()
    for s in new_splits:
        session.refresh(s)
    return new_splits


def get_splits(session: Session, transaction_id: str) -> list[TransactionSplit]:
    """Return all splits for a given transaction."""
    return (
        session.query(TransactionSplit)
        .filter(TransactionSplit.transaction_id == transaction_id)
        .order_by(TransactionSplit.created_at)
        .all()
    )


def delete_splits(session: Session, transaction_id: str) -> None:
    """Delete all splits for a given transaction."""
    session.query(TransactionSplit).filter(
        TransactionSplit.transaction_id == transaction_id
    ).delete(synchronize_session="fetch")
    session.commit()
