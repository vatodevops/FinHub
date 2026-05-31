"""AssetValue model for tracking historical valuations of assets."""

from __future__ import annotations

import enum
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin

if TYPE_CHECKING:
    from app.models.asset import Asset


class AssetValueSource(str, enum.Enum):
    manual = "manual"
    rule = "rule"
    sync = "sync"


class AssetValue(UUIDTimestampMixin, Base):
    __tablename__ = "asset_values"

    asset_id: Mapped[str] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[AssetValueSource] = mapped_column(
        Enum(AssetValueSource, name="asset_value_source"),
        nullable=False,
        default=AssetValueSource.manual,
    )

    # Relationships
    asset: Mapped[Asset] = relationship(back_populates="values", lazy="selectin")

    def __repr__(self) -> str:
        return f"<AssetValue(id={self.id}, asset_id={self.asset_id}, amount={self.amount}, date={self.date})>"
