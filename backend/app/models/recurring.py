import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin


class RecurrenceType(str, enum.Enum):
    weekly = "weekly"
    monthly = "monthly"
    bimonthly = "bimonthly"
    quarterly = "quarterly"
    yearly = "yearly"
    irregular = "irregular"


class RecurrenceState(str, enum.Enum):
    auto_detected = "auto_detected"
    manual_confirmed = "manual_confirmed"
    manual_ignored = "manual_ignored"
    inactive = "inactive"


class OccurrenceStatus(str, enum.Enum):
    expected = "expected"
    due = "due"
    paid = "paid"
    missed = "missed"
    skipped = "skipped"


class RecurringSeries(UUIDTimestampMixin, Base):
    __tablename__ = "recurring_series"

    account_id: Mapped[str | None] = mapped_column(ForeignKey("accounts.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    merchant_clean: Mapped[str | None] = mapped_column(String(255))
    channel: Mapped[str | None] = mapped_column(String(50))
    recurrence_type: Mapped[RecurrenceType] = mapped_column(Enum(RecurrenceType, name="recurrence_type"), nullable=False)
    interval_days: Mapped[int | None] = mapped_column(Integer)
    typical_day_of_month: Mapped[int | None] = mapped_column(Integer)
    amount_mean: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    amount_deviation: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    next_expected_date: Mapped[date | None] = mapped_column(Date)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    state: Mapped[RecurrenceState] = mapped_column(Enum(RecurrenceState, name="recurrence_state"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    account = relationship("Account")
    occurrences: Mapped[list["RecurringOccurrence"]] = relationship(back_populates="series")


class RecurringOccurrence(UUIDTimestampMixin, Base):
    __tablename__ = "recurring_occurrences"

    series_id: Mapped[str] = mapped_column(ForeignKey("recurring_series.id"), nullable=False)
    expected_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    matched_transaction_id: Mapped[str | None] = mapped_column(ForeignKey("transactions.id"))
    status: Mapped[OccurrenceStatus] = mapped_column(Enum(OccurrenceStatus, name="occurrence_status"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    series: Mapped[RecurringSeries] = relationship(back_populates="occurrences")
