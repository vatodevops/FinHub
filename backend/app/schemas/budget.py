import uuid
from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    category_name: str | None = None
    category_color: str | None = None
    amount_limit: Decimal
    spent: Decimal = Decimal("0.00")
    period: str
    month: int
    year: int

    model_config = {"from_attributes": True}


class CreateBudgetRequest(BaseModel):
    category_id: uuid.UUID
    amount_limit: Decimal = Field(gt=0)
    period: str = Field(default="monthly")
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2020, le=2100)


class UpdateBudgetRequest(BaseModel):
    amount_limit: Decimal | None = Field(default=None, gt=0)
    period: str | None = None
