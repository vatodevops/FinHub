from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class OverviewResponse(BaseModel):
    today: date
    account_count: int
    institution_count: int
    transaction_count: int
    booked_income_month: Decimal
    booked_expense_month: Decimal
    net_month: Decimal
    planned_expense_upcoming: Decimal
    recurring_due_upcoming: Decimal
