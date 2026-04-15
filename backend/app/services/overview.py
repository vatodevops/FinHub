from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.entities import Account, Institution, Transaction, TransactionStatus
from app.models.manual import ManualItemStatus, ManualPlannedItem
from app.models.recurring import OccurrenceStatus, RecurringOccurrence
from app.schemas.overview import OverviewResponse


ZERO = Decimal("0.00")


def build_overview(db: Session, user_id, today: date | None = None) -> OverviewResponse:
    today = today or date.today()
    month_start = today.replace(day=1)

    account_count = db.query(func.count(Account.id)).filter(Account.user_id == user_id).scalar() or 0
    institution_count = (
        db.query(func.count(Institution.id)).filter(Institution.user_id == user_id).scalar() or 0
    )
    transaction_count = (
        db.query(func.count(Transaction.id)).filter(Transaction.user_id == user_id).scalar() or 0
    )

    month_rows = (
        db.query(Transaction.amount)
        .filter(Transaction.user_id == user_id)
        .filter(Transaction.value_date >= month_start)
        .filter(Transaction.value_date <= today)
        .filter(Transaction.status.in_([TransactionStatus.booked, TransactionStatus.pending]))
        .all()
    )

    booked_income = sum((row[0] for row in month_rows if row[0] > 0), ZERO)
    booked_expense = sum((abs(row[0]) for row in month_rows if row[0] < 0), ZERO)
    net_month = booked_income - booked_expense

    upcoming_until = today + timedelta(days=30)

    planned_expense_upcoming = sum(
        (
            row[0]
            for row in db.query(ManualPlannedItem.amount)
            .filter(ManualPlannedItem.user_id == user_id)
            .filter(ManualPlannedItem.status == ManualItemStatus.planned)
            .filter(ManualPlannedItem.expected_date >= today)
            .filter(ManualPlannedItem.expected_date <= upcoming_until)
            .all()
            if row[0] is not None
        ),
        ZERO,
    )

    recurring_due_upcoming = sum(
        (
            row[0]
            for row in db.query(RecurringOccurrence.expected_amount)
            .filter(RecurringOccurrence.user_id == user_id)
            .filter(RecurringOccurrence.status.in_([OccurrenceStatus.expected, OccurrenceStatus.due]))
            .filter(RecurringOccurrence.expected_date >= today)
            .filter(RecurringOccurrence.expected_date <= upcoming_until)
            .all()
            if row[0] is not None
        ),
        ZERO,
    )

    return OverviewResponse(
        today=today,
        account_count=account_count,
        institution_count=institution_count,
        transaction_count=transaction_count,
        booked_income_month=booked_income.quantize(Decimal("0.01")),
        booked_expense_month=booked_expense.quantize(Decimal("0.01")),
        net_month=net_month.quantize(Decimal("0.01")),
        planned_expense_upcoming=planned_expense_upcoming.quantize(Decimal("0.01")),
        recurring_due_upcoming=recurring_due_upcoming.quantize(Decimal("0.01")),
    )
