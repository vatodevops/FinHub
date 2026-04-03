import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class TransactionResponse(BaseModel):
    id: uuid.UUID
    account_id: uuid.UUID
    category_id: uuid.UUID | None
    category_name: str | None = None
    source_type: str
    source_id: str
    amount: Decimal
    currency: str
    booked_at: datetime | None
    value_date: date | None
    merchant_raw: str | None
    merchant_clean: str | None
    description_raw: str | None
    channel: str
    status: str

    model_config = {"from_attributes": True}
