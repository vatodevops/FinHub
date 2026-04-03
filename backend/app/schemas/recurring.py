import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class RecurringSeriesResponse(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID | None
    name: str
    merchant_clean: str | None
    recurrence_type: str
    interval_days: int | None
    typical_day_of_month: int | None
    amount_mean: Decimal | None
    next_expected_date: date | None
    confidence: Decimal | None
    state: str

    model_config = {"from_attributes": True}


class RecurringOccurrenceResponse(BaseModel):
    id: uuid.UUID
    series_id: uuid.UUID
    expected_date: date
    expected_amount: Decimal | None
    status: str
    matched_transaction_id: uuid.UUID | None

    model_config = {"from_attributes": True}
