from decimal import Decimal

from pydantic import BaseModel


class MonthlySummaryItem(BaseModel):
    month: str
    income: Decimal
    expense: Decimal
    net: Decimal


class CategoryBreakdownItem(BaseModel):
    category_id: str | None
    category_name: str
    category_color: str | None
    total: Decimal
    percentage: float


class NetWorthPoint(BaseModel):
    month: str
    total: Decimal
