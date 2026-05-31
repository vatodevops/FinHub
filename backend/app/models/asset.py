"""Asset model for tracking investments, real estate, vehicles, and valuables."""

from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin

if TYPE_CHECKING:
    from app.models.asset_group import AssetGroup
    from app.models.asset_value import AssetValue


class AssetType(str, enum.Enum):
    real_estate = "real_estate"
    vehicle = "vehicle"
    valuable = "valuable"
    investment = "investment"
    other = "other"


class ValuationMethod(str, enum.Enum):
    manual = "manual"
    growth_rule = "growth_rule"
    market_price = "market_price"


class GrowthFrequency(str, enum.Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class GrowthType(str, enum.Enum):
    percentage = "percentage"
    absolute = "absolute"


class AssetSource(str, enum.Enum):
    manual = "manual"
    sync = "sync"


class Asset(UUIDTimestampMixin, Base):
    __tablename__ = "assets"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[AssetType] = mapped_column(
        Enum(AssetType, name="asset_type"), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    units: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    valuation_method: Mapped[ValuationMethod] = mapped_column(
        Enum(ValuationMethod, name="valuation_method"), nullable=False, default=ValuationMethod.manual
    )
    purchase_date: Mapped[date | None] = mapped_column(Date)
    purchase_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    sell_date: Mapped[date | None] = mapped_column(Date)
    sell_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    growth_type: Mapped[GrowthType | None] = mapped_column(Enum(GrowthType, name="growth_type"))
    growth_rate: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))
    growth_frequency: Mapped[GrowthFrequency | None] = mapped_column(
        Enum(GrowthFrequency, name="growth_frequency")
    )
    growth_start_date: Mapped[date | None] = mapped_column(Date)
    is_archived: Mapped[bool] = mapped_column(default=False)
    ticker: Mapped[str | None] = mapped_column(String(32))
    ticker_exchange: Mapped[str | None] = mapped_column(String(64))
    last_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    last_price_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    logo_url: Mapped[str | None] = mapped_column(String(512))
    external_id: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[AssetSource] = mapped_column(
        Enum(AssetSource, name="asset_source"), nullable=False, default=AssetSource.manual
    )
    external_metadata: Mapped[dict | None] = mapped_column(Text, default=None)

    # Relationships
    values: Mapped[list[AssetValue]] = relationship(
        back_populates="asset", cascade="all, delete-orphan", lazy="selectin"
    )
    group: Mapped[AssetGroup | None] = relationship(back_populates="assets", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Asset(id={self.id}, name={self.name!r}, type={self.type.value})>"


# Forward reference for AssetValue relationship
if TYPE_CHECKING:
    Asset.value_set = relationship("AssetValue", back_populates="asset")
