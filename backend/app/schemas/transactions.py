from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.models.entities import Transaction


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


def tx_payload(tx: Transaction) -> dict:
    return {
        "id": tx.id,
        "account_id": tx.account_id,
        "category_id": tx.category_id,
        "category_name": tx.category.name if getattr(tx, "category", None) else None,
        "source_type": tx.source_type.value if hasattr(tx.source_type, "value") else tx.source_type,
        "source_id": tx.source_id,
        "amount": tx.amount,
        "currency": tx.currency,
        "booked_at": tx.booked_at,
        "value_date": tx.value_date,
        "merchant_raw": tx.merchant_raw,
        "merchant_clean": tx.merchant_clean,
        "description_raw": tx.description_raw,
        "channel": tx.channel.value if hasattr(tx.channel, "value") else tx.channel,
        "status": tx.status.value if hasattr(tx.status, "value") else tx.status,
    }
