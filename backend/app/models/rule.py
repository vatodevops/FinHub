import uuid

from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.common import UUIDTimestampMixin


class Rule(UUIDTimestampMixin, Base):
    __tablename__ = "rules"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    conditions_op: Mapped[str] = mapped_column(String(3), nullable=False, default="and")
    conditions: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    actions: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    priority: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
