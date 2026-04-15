import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin


class ManualItemKind(str, enum.Enum):
    one_off = "one_off"
    recurring = "recurring"


class ManualItemStatus(str, enum.Enum):
    planned = "planned"
    paid = "paid"
    skipped = "skipped"
    cancelled = "cancelled"


class ManualPlannedItem(UUIDTimestampMixin, Base):
    __tablename__ = "manual_planned_items"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    merchant_hint: Mapped[str | None] = mapped_column(String(255))
    kind: Mapped[ManualItemKind] = mapped_column(Enum(ManualItemKind, name="manual_item_kind"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    expected_date: Mapped[date | None] = mapped_column(Date)
    recurrence_rule: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[ManualItemStatus] = mapped_column(Enum(ManualItemStatus, name="manual_item_status"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    account = relationship("Account")
