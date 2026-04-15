import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.auth import User
from app.models.entities import Account
from app.models.manual import ManualItemKind, ManualItemStatus, ManualPlannedItem
from app.schemas.manual import ManualPlannedItemCreate, ManualPlannedItemResponse

router = APIRouter()


@router.get("/manual/planned-items", response_model=list[ManualPlannedItemResponse])
def list_manual_planned_items(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[ManualPlannedItemResponse]:
    return (
        db.query(ManualPlannedItem)
        .filter(ManualPlannedItem.user_id == user.id)
        .order_by(ManualPlannedItem.expected_date.asc().nullslast())
        .all()
    )


@router.post("/manual/planned-items", response_model=ManualPlannedItemResponse)
def create_manual_planned_item(
    payload: ManualPlannedItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> ManualPlannedItemResponse:
    if payload.account_id:
        account = (
            db.query(Account)
            .filter(Account.id == payload.account_id, Account.user_id == user.id)
            .one_or_none()
        )
        if not account:
            raise NotFoundError("account_not_found")

    item = ManualPlannedItem(
        user_id=user.id,
        account_id=payload.account_id,
        name=payload.name,
        merchant_hint=payload.merchant_hint,
        kind=ManualItemKind(payload.kind),
        amount=payload.amount,
        currency=payload.currency,
        expected_date=payload.expected_date,
        recurrence_rule=payload.recurrence_rule,
        status=ManualItemStatus(payload.status),
        notes=payload.notes,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/manual/planned-items/{item_id}", status_code=204)
def delete_manual_planned_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
):
    item = (
        db.query(ManualPlannedItem)
        .filter(ManualPlannedItem.id == item_id, ManualPlannedItem.user_id == user.id)
        .one_or_none()
    )
    if not item:
        raise NotFoundError("manual_item_not_found")
    db.delete(item)
    db.commit()
