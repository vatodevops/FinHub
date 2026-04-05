from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.manual import ManualItemKind, ManualItemStatus, ManualPlannedItem
from app.schemas.manual import ManualPlannedItemCreate, ManualPlannedItemResponse

router = APIRouter()


@router.get("/manual/planned-items", response_model=list[ManualPlannedItemResponse])
def list_manual_planned_items(db: Session = Depends(get_db)) -> list[ManualPlannedItemResponse]:
    return db.query(ManualPlannedItem).order_by(ManualPlannedItem.expected_date.asc().nullslast()).all()


@router.post("/manual/planned-items", response_model=ManualPlannedItemResponse)
def create_manual_planned_item(payload: ManualPlannedItemCreate, db: Session = Depends(get_db)) -> ManualPlannedItemResponse:
    item = ManualPlannedItem(
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
