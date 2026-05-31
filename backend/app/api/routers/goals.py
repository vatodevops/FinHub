import uuid
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.auth import User
from app.models.goal import GoalStatus
from app.services import goal_service

router = APIRouter(dependencies=[Depends(require_auth)])


# ── Pydantic schemas ──────────────────────────────────────────────

class CreateGoalRequest(BaseModel):
    name: str
    target_amount: Decimal
    currency: str = "EUR"
    target_date: date | None = None
    tracking_type: str = "manual"
    account_id: str | None = None
    asset_id: str | None = None
    icon: str | None = None
    color: str | None = None
    position: int = 0


class UpdateGoalRequest(BaseModel):
    name: str | None = None
    target_amount: Decimal | None = None
    current_amount: Decimal | None = None
    currency: str | None = None
    target_date: date | None = None
    tracking_type: str | None = None
    account_id: str | None = None
    asset_id: str | None = None
    status: str | None = None
    icon: str | None = None
    color: str | None = None
    position: int | None = None


class ContributeRequest(BaseModel):
    amount: Decimal


class GoalResponse(BaseModel):
    id: str
    name: str
    target_amount: Decimal
    current_amount: Decimal
    currency: str
    target_date: date | None
    tracking_type: str
    account_id: str | None
    asset_id: str | None
    status: str
    icon: str | None
    color: str | None
    position: int
    progress_percentage: Decimal

    model_config = {"from_attributes": True}


# ── Helpers ───────────────────────────────────────────────────────

def _goal_to_response(goal) -> dict:
    return {
        "id": str(goal.id),
        "name": goal.name,
        "target_amount": goal.target_amount,
        "current_amount": goal.current_amount,
        "currency": goal.currency,
        "target_date": goal.target_date,
        "tracking_type": goal.tracking_type.value if hasattr(goal.tracking_type, "value") else str(goal.tracking_type),
        "account_id": str(goal.account_id) if goal.account_id else None,
        "asset_id": str(goal.asset_id) if goal.asset_id else None,
        "status": goal.status.value if hasattr(goal.status, "value") else str(goal.status),
        "icon": goal.icon,
        "color": goal.color,
        "position": goal.position,
        "progress_percentage": goal_service.progress_percentage(goal),
    }


# ── Routes ────────────────────────────────────────────────────────

@router.get("", response_model=list[GoalResponse])
def list_goals(
    status: GoalStatus | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[GoalResponse]:
    goals = goal_service.get_goals(db, user.id, status=status)
    return [_goal_to_response(g) for g in goals]


@router.post("", response_model=GoalResponse, status_code=201)
def create_goal(
    payload: CreateGoalRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> GoalResponse:
    data = payload.model_dump(exclude_none=True)
    goal = goal_service.create_goal(db, user.id, **data)
    return _goal_to_response(goal)


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> GoalResponse:
    goal = goal_service.get_goal(db, str(goal_id), user.id)
    if goal is None:
        raise NotFoundError("goal_not_found")
    return _goal_to_response(goal)


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: uuid.UUID,
    payload: UpdateGoalRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> GoalResponse:
    data = payload.model_dump(exclude_none=True)
    goal = goal_service.update_goal(db, str(goal_id), user.id, **data)
    return _goal_to_response(goal)


@router.delete("/{goal_id}", status_code=204)
def archive_goal(
    goal_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
):
    goal_service.delete_goal(db, str(goal_id), user.id)


@router.post("/{goal_id}/contribute", response_model=GoalResponse, status_code=201)
def contribute_to_goal(
    goal_id: uuid.UUID,
    payload: ContributeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> GoalResponse:
    goal = goal_service.add_contribution(db, str(goal_id), user.id, payload.amount)
    return _goal_to_response(goal)
