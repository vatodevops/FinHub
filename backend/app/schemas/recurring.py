import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


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


class CreateRecurringSeriesRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    account_id: uuid.UUID | None = None
    merchant_clean: str | None = None
    recurrence_type: str = Field(default="monthly")
    typical_day_of_month: int | None = Field(default=None, ge=1, le=31)
    amount_mean: Decimal | None = None
    next_expected_date: date | None = None
    notes: str | None = None


class UpdateRecurringSeriesRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    recurrence_type: str | None = None
    typical_day_of_month: int | None = Field(default=None, ge=1, le=31)
    amount_mean: Decimal | None = None
    next_expected_date: date | None = None
    state: str | None = None
    notes: str | None = None
