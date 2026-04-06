import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class AccountResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    name: str
    iban_masked: str | None
    currency: str
    kind: str
    is_active: bool
    institution_name: str | None = None
    balance: str | None = None

    model_config = {"from_attributes": True}


class CreateAccountRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    kind: str = Field(description="checking, savings, credit_card, investment, cash")
    currency: str = Field(default="EUR", max_length=3)
    initial_balance: Decimal = Field(default=Decimal("0.00"))
    iban: str | None = Field(default=None, max_length=64)
    institution_name: str | None = Field(default=None, max_length=255)


class UpdateAccountRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    kind: str | None = None
    currency: str | None = Field(default=None, max_length=3)
    iban: str | None = None
    is_active: bool | None = None
    institution_name: str | None = None
