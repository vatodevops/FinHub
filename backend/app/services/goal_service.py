"""Goal / Savings Target CRUD service."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import NotFoundError
from app.models.goal import Goal, GoalStatus, TrackingType

if TYPE_CHECKING:
    from app.models.account import Account  # noqa: F401
    from app.models.asset import Asset  # noqa: F401


def create_goal(session: Session, user_id: str, **data) -> Goal:
    """Create a new goal for the given user."""
    if "currency" not in data or data["currency"] is None:
        data["currency"] = "EUR"
    if "status" not in data or data["status"] is None:
        data["status"] = GoalStatus.active
    if "tracking_type" not in data or data["tracking_type"] is None:
        data["tracking_type"] = TrackingType.manual
    if "current_amount" not in data:
        data["current_amount"] = Decimal("0")
    if "position" not in data:
        data["position"] = 0

    goal = Goal(user_id=user_id, **data)
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal


def get_goal(session: Session, goal_id: str, user_id: str) -> Goal | None:
    """Get a single goal by id, scoped to user."""
    stmt = (
        select(Goal)
        .where(Goal.id == goal_id, Goal.user_id == user_id)
        .options(selectinload(Goal.account), selectinload(Goal.asset))
    )
    return session.execute(stmt).scalar_one_or_none()


def get_goals(
    session: Session,
    user_id: str,
    status: GoalStatus | None = None,
) -> list[Goal]:
    """List goals for a user with optional status filter."""
    stmt = select(Goal).where(Goal.user_id == user_id)

    if status is not None:
        stmt = stmt.where(Goal.status == status)

    stmt = stmt.order_by(Goal.position.asc(), Goal.created_at.asc())
    return list(session.execute(stmt).scalars().all())


def update_goal(session: Session, goal_id: str, user_id: str, **data) -> Goal:
    """Update an existing goal (must belong to user)."""
    stmt = (
        select(Goal)
        .where(Goal.id == goal_id, Goal.user_id == user_id)
        .options(selectinload(Goal.account), selectinload(Goal.asset))
    )
    goal = session.execute(stmt).scalar_one_or_none()

    if goal is None:
        raise NotFoundError("goal_not_found")

    updatable = {
        "name",
        "target_amount",
        "current_amount",
        "currency",
        "target_date",
        "tracking_type",
        "account_id",
        "asset_id",
        "status",
        "icon",
        "color",
        "position",
    }

    for key, value in data.items():
        if key in updatable:
            setattr(goal, key, value)

    session.commit()
    session.refresh(goal)
    return goal


def delete_goal(session: Session, goal_id: str, user_id: str) -> Goal:
    """Soft-delete a goal by setting status to archived."""
    stmt = (
        select(Goal)
        .where(Goal.id == goal_id, Goal.user_id == user_id)
        .options(selectinload(Goal.account), selectinload(Goal.asset))
    )
    goal = session.execute(stmt).scalar_one_or_none()

    if goal is None:
        raise NotFoundError("goal_not_found")

    goal.status = GoalStatus.archived
    session.commit()
    session.refresh(goal)
    return goal


def progress_percentage(goal: Goal) -> Decimal:
    """Calculate progress percentage: (current / target) * 100."""
    if goal.target_amount <= 0:
        return Decimal("0")
    return (goal.current_amount / goal.target_amount) * Decimal("100")


def add_contribution(session: Session, goal_id: str, user_id: str, amount: Decimal) -> Goal:
    """Add a contribution to a goal, incrementing current_amount."""
    stmt = (
        select(Goal)
        .where(Goal.id == goal_id, Goal.user_id == user_id)
        .options(selectinload(Goal.account), selectinload(Goal.asset))
    )
    goal = session.execute(stmt).scalar_one_or_none()

    if goal is None:
        raise NotFoundError("goal_not_found")

    goal.current_amount = goal.current_amount + amount

    # Auto-complete if target reached
    if goal.current_amount >= goal.target_amount and goal.status == GoalStatus.active:
        goal.status = GoalStatus.completed

    session.commit()
    session.refresh(goal)
    return goal
