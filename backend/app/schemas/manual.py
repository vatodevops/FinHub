import uuid
from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class ManualPlannedItemResponse(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID | None
    name: str
    merchant_hint: str | None
    kind: str
    amount: Decimal
    currency: str
    expected_date: date | None
    recurrence_rule: str | None
    status: str
    notes: str | None

    model_config = {"from_attributes": True}


class ManualPlannedItemCreate(BaseModel):
    account_id: uuid.UUID | None = None
    name: str
    merchant_hint: str | None = None
    kind: str
    amount: Decimal
    currency: str = "EUR"
    expected_date: date | None = None
    recurrence_rule: str | None = None
    status: str = "planned"
    notes: str | None = None
