import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.auth import User
from app.services import asset_group_service

router = APIRouter(dependencies=[Depends(require_auth)])


# ── Pydantic schemas ──────────────────────────────────────────────

class CreateGroupRequest(BaseModel):
    name: str
    description: str | None = None
    position: int = 0


class UpdateGroupRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    position: int | None = None


class AssetGroupResponse(BaseModel):
    id: str
    name: str
    description: str | None
    position: int
    created_at: str | None
    updated_at: str | None

    model_config = {"from_attributes": True}


# ── Helpers ───────────────────────────────────────────────────────

def _group_to_response(group) -> dict:
    return {
        "id": str(group.id),
        "name": group.name,
        "description": group.description,
        "position": group.position,
        "created_at": str(group.created_at) if group.created_at else None,
        "updated_at": str(group.updated_at) if group.updated_at else None,
    }


# ── Routes ────────────────────────────────────────────────────────

@router.get("", response_model=list[AssetGroupResponse])
def list_groups(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[AssetGroupResponse]:
    groups = asset_group_service.get_groups(db, user.id)
    return [_group_to_response(g) for g in groups]


@router.post("", response_model=AssetGroupResponse, status_code=201)
def create_group(
    payload: CreateGroupRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> AssetGroupResponse:
    group = asset_group_service.create_group(
        db, user.id, name=payload.name, description=payload.description
    )
    return _group_to_response(group)


@router.put("/{group_id}", response_model=AssetGroupResponse)
def update_group(
    group_id: uuid.UUID,
    payload: UpdateGroupRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> AssetGroupResponse:
    data = payload.model_dump(exclude_none=True)
    group = asset_group_service.update_group(db, str(group_id), user.id, **data)
    return _group_to_response(group)


@router.delete("/{group_id}", status_code=204)
def delete_group(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
):
    asset_group_service.delete_group(db, str(group_id), user.id)
