import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin


class BankConnectionStatus(str, enum.Enum):
    pending = "pending"
    linked = "linked"
    expired = "expired"
    failed = "failed"


class BankConnection(UUIDTimestampMixin, Base):
    __tablename__ = "bank_connections"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_id: Mapped[str | None] = mapped_column(ForeignKey("institutions.id"))
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    requisition_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    reference: Mapped[str] = mapped_column(String(255), nullable=False)
    institution_external_id: Mapped[str | None] = mapped_column(String(255))
    institution_name: Mapped[str | None] = mapped_column(String(255))
    link: Mapped[str | None] = mapped_column(Text)
    status: Mapped[BankConnectionStatus] = mapped_column(Enum(BankConnectionStatus, name="bank_connection_status"), nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text)

    institution = relationship("Institution")
