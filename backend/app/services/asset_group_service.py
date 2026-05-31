"""AssetGroup CRUD service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import NotFoundError
from app.models.asset_group import AssetGroup

if TYPE_CHECKING:
    from app.models.asset import Asset


def create_group(session: Session, user_id: str, name: str, description: str | None = None) -> AssetGroup:
    """Create a new asset group for the given user."""
    group = AssetGroup(user_id=user_id, name=name, description=description)
    session.add(group)
    session.commit()
    session.refresh(group)
    return group


def get_groups(session: Session, user_id: str) -> list[AssetGroup]:
    """List all asset groups for a user, ordered by position."""
    stmt = (
        select(AssetGroup)
        .where(AssetGroup.user_id == user_id)
        .options(selectinload(AssetGroup.assets))
        .order_by(AssetGroup.position.asc(), AssetGroup.created_at.asc())
    )
    return list(session.execute(stmt).scalars().all())


def update_group(
    session: Session,
    group_id: str,
    user_id: str,
    **data,
) -> AssetGroup:
    """Update an existing asset group (must belong to user)."""
    stmt = (
        select(AssetGroup)
        .where(AssetGroup.id == group_id, AssetGroup.user_id == user_id)
        .options(selectinload(AssetGroup.assets))
    )
    group = session.execute(stmt).scalar_one_or_none()

    if group is None:
        raise NotFoundError("asset_group_not_found")

    updatable = {"name", "description", "position"}
    for key, value in data.items():
        if key in updatable:
            setattr(group, key, value)

    session.commit()
    session.refresh(group)
    return group


def delete_group(session: Session, group_id: str, user_id: str) -> None:
    """Delete an asset group (must belong to user)."""
    stmt = (
        select(AssetGroup)
        .where(AssetGroup.id == group_id, AssetGroup.user_id == user_id)
    )
    group = session.execute(stmt).scalar_one_or_none()

    if group is None:
        raise NotFoundError("asset_group_not_found")

    session.delete(group)
    session.commit()
