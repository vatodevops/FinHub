"""Goal / Savings Target model for tracking savings and financial goals."""

from __future__ import annotations

import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin


class TrackingType(str, enum.Enum):
    manual = "manual"
    account = "account"
    asset = "asset"
    net_worth = "net_worth"


class GoalStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    paused = "paused"
    archived = "archived"


class Goal(UUIDTimestampMixin, Base):
    __tablename__ = "goals"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    current_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False, default=Decimal("0"))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    target_date: Mapped[date | None] = mapped_column(Date)
    tracking_type: Mapped[TrackingType] = mapped_column(
        Enum(TrackingType, name="tracking_type"), nullable=False, default=TrackingType.manual
    )
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"))
    asset_id: Mapped[str | None] = mapped_column(ForeignKey("assets.id"))
    status: Mapped[GoalStatus] = mapped_column(
        Enum(GoalStatus, name="goal_status"), nullable=False, default=GoalStatus.active
    )
    icon: Mapped[str | None] = mapped_column(String(32))
    color: Mapped[str | None] = mapped_column(String(32))
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    user = relationship("User")
    account = relationship("Account", foreign_keys=[account_id])
    asset = relationship("Asset", foreign_keys=[asset_id])

    def __repr__(self) -> str:
        return f"<Goal(id={self.id}, name={self.name!r}, status={self.status.value})>"
