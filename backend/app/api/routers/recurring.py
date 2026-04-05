import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Transaction
from app.models.recurring import RecurringOccurrence, RecurringSeries
from app.schemas.recurring import RecurringOccurrenceResponse, RecurringSeriesResponse
from app.services.recurring_detection import detect_monthly_candidates

router = APIRouter()


@router.get("/recurring/series", response_model=list[RecurringSeriesResponse])
def list_recurring_series(db: Session = Depends(get_db)) -> list[RecurringSeriesResponse]:
    return db.query(RecurringSeries).order_by(RecurringSeries.next_expected_date.asc().nullslast()).all()


@router.get("/recurring/calendar", response_model=list[RecurringOccurrenceResponse])
def recurring_calendar(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[RecurringOccurrenceResponse]:
    return (
        db.query(RecurringOccurrence)
        .order_by(RecurringOccurrence.expected_date.asc(), RecurringOccurrence.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/recurring/suggestions")
def recurring_suggestions(
    account_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    txs = query.all()
    return detect_monthly_candidates(txs)
