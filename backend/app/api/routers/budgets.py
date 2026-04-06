import uuid
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.budget import Budget, BudgetPeriod
from app.models.categories import Category
from app.models.entities import Transaction, TransactionStatus
from app.schemas.budget import BudgetResponse, CreateBudgetRequest, UpdateBudgetRequest

router = APIRouter()


def _budget_to_response(budget: Budget, db: Session) -> dict:
    start = datetime(budget.year, budget.month, 1, tzinfo=timezone.utc)
    if budget.month == 12:
        end = datetime(budget.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(budget.year, budget.month + 1, 1, tzinfo=timezone.utc)

    spent = db.query(func.coalesce(func.sum(func.abs(Transaction.amount)), 0)).filter(
        Transaction.category_id == budget.category_id,
        Transaction.amount < 0,
        Transaction.status.in_([TransactionStatus.booked, TransactionStatus.pending]),
        Transaction.booked_at >= start,
        Transaction.booked_at < end,
    ).scalar()

    cat = db.query(Category).filter(Category.id == budget.category_id).first()
    return {
        "id": budget.id,
        "category_id": budget.category_id,
        "category_name": cat.name if cat else None,
        "category_color": cat.color if cat else None,
        "amount_limit": budget.amount_limit,
        "spent": spent,
        "period": budget.period.value if isinstance(budget.period, BudgetPeriod) else budget.period,
        "month": budget.month,
        "year": budget.year,
    }


@router.get("/budgets", response_model=list[BudgetResponse])
def list_budgets(
    month: int = Query(default=None, ge=1, le=12),
    year: int = Query(default=None, ge=2020, le=2100),
    db: Session = Depends(get_db),
) -> list[BudgetResponse]:
    from datetime import date

    if month is None:
        month = date.today().month
    if year is None:
        year = date.today().year

    budgets = db.query(Budget).filter(Budget.month == month, Budget.year == year).all()
    return [_budget_to_response(b, db) for b in budgets]


@router.post("/budgets", response_model=BudgetResponse, status_code=201)
def create_budget(payload: CreateBudgetRequest, db: Session = Depends(get_db)) -> BudgetResponse:
    cat = db.query(Category).filter(Category.id == payload.category_id).first()
    if not cat:
        raise NotFoundError("category_not_found")

    try:
        period = BudgetPeriod(payload.period)
    except ValueError:
        period = BudgetPeriod.monthly

    budget = Budget(
        category_id=payload.category_id,
        amount_limit=payload.amount_limit,
        period=period,
        month=payload.month,
        year=payload.year,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return _budget_to_response(budget, db)


@router.patch("/budgets/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: uuid.UUID,
    payload: UpdateBudgetRequest,
    db: Session = Depends(get_db),
) -> BudgetResponse:
    budget = db.query(Budget).filter(Budget.id == budget_id).one_or_none()
    if not budget:
        raise NotFoundError("budget_not_found")
    if payload.amount_limit is not None:
        budget.amount_limit = payload.amount_limit
    if payload.period is not None:
        try:
            budget.period = BudgetPeriod(payload.period)
        except ValueError:
            pass
    db.commit()
    db.refresh(budget)
    return _budget_to_response(budget, db)


@router.delete("/budgets/{budget_id}", status_code=204)
def delete_budget(budget_id: uuid.UUID, db: Session = Depends(get_db)):
    budget = db.query(Budget).filter(Budget.id == budget_id).one_or_none()
    if not budget:
        raise NotFoundError("budget_not_found")
    db.delete(budget)
    db.commit()
