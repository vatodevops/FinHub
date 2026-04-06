import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.entities import Transaction
from app.models.recurring import RecurrenceState, RecurrenceType, RecurringOccurrence, RecurringSeries
from app.schemas.recurring import (
    CreateRecurringSeriesRequest,
    RecurringOccurrenceResponse,
    RecurringSeriesResponse,
    UpdateRecurringSeriesRequest,
)
from app.services.recurring_detection import detect_monthly_candidates

router = APIRouter()


@router.get("/recurring/series", response_model=list[RecurringSeriesResponse])
def list_recurring_series(db: Session = Depends(get_db)) -> list[RecurringSeriesResponse]:
    return db.query(RecurringSeries).order_by(RecurringSeries.next_expected_date.asc().nullslast()).all()


@router.post("/recurring/series", response_model=RecurringSeriesResponse, status_code=201)
def create_recurring_series(payload: CreateRecurringSeriesRequest, db: Session = Depends(get_db)):
    try:
        rec_type = RecurrenceType(payload.recurrence_type)
    except ValueError:
        rec_type = RecurrenceType.monthly

    series = RecurringSeries(
        account_id=payload.account_id,
        name=payload.name,
        merchant_clean=payload.merchant_clean,
        recurrence_type=rec_type,
        typical_day_of_month=payload.typical_day_of_month,
        amount_mean=payload.amount_mean,
        next_expected_date=payload.next_expected_date,
        state=RecurrenceState.manual_confirmed,
        notes=payload.notes,
    )
    db.add(series)
    db.commit()
    db.refresh(series)
    return series


@router.patch("/recurring/series/{series_id}", response_model=RecurringSeriesResponse)
def update_recurring_series(
    series_id: uuid.UUID,
    payload: UpdateRecurringSeriesRequest,
    db: Session = Depends(get_db),
):
    series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).one_or_none()
    if not series:
        raise NotFoundError("series_not_found")

    if payload.name is not None:
        series.name = payload.name
    if payload.recurrence_type is not None:
        try:
            series.recurrence_type = RecurrenceType(payload.recurrence_type)
        except ValueError:
            pass
    if payload.typical_day_of_month is not None:
        series.typical_day_of_month = payload.typical_day_of_month
    if payload.amount_mean is not None:
        series.amount_mean = payload.amount_mean
    if payload.next_expected_date is not None:
        series.next_expected_date = payload.next_expected_date
    if payload.state is not None:
        try:
            series.state = RecurrenceState(payload.state)
        except ValueError:
            pass
    if payload.notes is not None:
        series.notes = payload.notes

    db.commit()
    db.refresh(series)
    return series


@router.delete("/recurring/series/{series_id}", status_code=204)
def delete_recurring_series(series_id: uuid.UUID, db: Session = Depends(get_db)):
    series = db.query(RecurringSeries).filter(RecurringSeries.id == series_id).one_or_none()
    if not series:
        raise NotFoundError("series_not_found")
    db.query(RecurringOccurrence).filter(RecurringOccurrence.series_id == series_id).delete()
    db.delete(series)
    db.commit()


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
