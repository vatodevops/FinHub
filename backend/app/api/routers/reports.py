from datetime import date, datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.db.session import get_db
from app.models.auth import User
from app.models.categories import Category
from app.models.entities import Transaction, TransactionStatus
from app.schemas.reports import CategoryBreakdownItem, MonthlySummaryItem, NetWorthPoint

router = APIRouter()


@router.get("/reports/monthly-summary", response_model=list[MonthlySummaryItem])
def monthly_summary(
    months: int = Query(default=6, ge=1, le=24),
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[MonthlySummaryItem]:
    today = date.today()
    results = []

    for i in range(months - 1, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1

        start = datetime(y, m, 1, tzinfo=timezone.utc)
        if m == 12:
            end = datetime(y + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(y, m + 1, 1, tzinfo=timezone.utc)

        base = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.status.in_([TransactionStatus.booked, TransactionStatus.pending]),
            Transaction.booked_at >= start,
            Transaction.booked_at < end,
        )

        income = base.filter(Transaction.amount > 0).with_entities(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).scalar()

        expense = base.filter(Transaction.amount < 0).with_entities(
            func.coalesce(func.sum(func.abs(Transaction.amount)), 0)
        ).scalar()

        results.append(MonthlySummaryItem(
            month=f"{y}-{m:02d}",
            income=income,
            expense=expense,
            net=income - expense,
        ))

    return results


@router.get("/reports/by-category", response_model=list[CategoryBreakdownItem])
def by_category(
    month: str = Query(default=None, description="YYYY-MM"),
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[CategoryBreakdownItem]:
    today = date.today()
    if month:
        parts = month.split("-")
        y, m = int(parts[0]), int(parts[1])
    else:
        y, m = today.year, today.month

    start = datetime(y, m, 1, tzinfo=timezone.utc)
    if m == 12:
        end = datetime(y + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(y, m + 1, 1, tzinfo=timezone.utc)

    rows = (
        db.query(
            Transaction.category_id,
            func.sum(func.abs(Transaction.amount)).label("total"),
        )
        .filter(
            Transaction.user_id == user.id,
            Transaction.amount < 0,
            Transaction.status.in_([TransactionStatus.booked, TransactionStatus.pending]),
            Transaction.booked_at >= start,
            Transaction.booked_at < end,
        )
        .group_by(Transaction.category_id)
        .all()
    )

    grand_total = sum(r.total for r in rows) or Decimal("1")
    categories = {
        c.id: c
        for c in db.query(Category).filter(Category.user_id == user.id).all()
    }
    result = []
    for row in rows:
        cat = categories.get(row.category_id)
        result.append(CategoryBreakdownItem(
            category_id=str(row.category_id) if row.category_id else None,
            category_name=cat.name if cat else "Sin categoria",
            category_color=cat.color if cat else "#888888",
            total=row.total,
            percentage=round(float(row.total / grand_total * 100), 1),
        ))
    result.sort(key=lambda x: x.total, reverse=True)
    return result


@router.get("/reports/net-worth", response_model=list[NetWorthPoint])
def net_worth(
    months: int = Query(default=12, ge=1, le=60),
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[NetWorthPoint]:
    today = date.today()
    results = []

    for i in range(months - 1, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1

        if m == 12:
            end = datetime(y + 1, 1, 1, tzinfo=timezone.utc)
        else:
            end = datetime(y, m + 1, 1, tzinfo=timezone.utc)

        total = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == user.id,
            Transaction.status.in_([TransactionStatus.booked, TransactionStatus.pending]),
            Transaction.booked_at < end,
        ).scalar()

        results.append(NetWorthPoint(
            month=f"{y}-{m:02d}",
            total=total,
        ))

    return results
