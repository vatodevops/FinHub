import enum
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin


class BudgetPeriod(str, enum.Enum):
    monthly = "monthly"
    weekly = "weekly"
    yearly = "yearly"


class Budget(UUIDTimestampMixin, Base):
    __tablename__ = "budgets"

    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"), nullable=False)
    amount_limit: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    period: Mapped[BudgetPeriod] = mapped_column(Enum(BudgetPeriod, name="budget_period"), nullable=False, default=BudgetPeriod.monthly)
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    category = relationship("Category")
