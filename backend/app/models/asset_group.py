"""AssetGroup model for organizing assets into user-defined groups."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin

if TYPE_CHECKING:
    from app.models.asset import Asset


class AssetGroup(UUIDTimestampMixin, Base):
    __tablename__ = "asset_groups"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    position: Mapped[int] = mapped_column(default=0)

    # Relationships
    assets: Mapped[list[Asset]] = relationship(
        back_populates="group", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<AssetGroup(id={self.id}, name={self.name!r})>"
