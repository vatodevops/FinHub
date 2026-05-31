from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.auth import User
from app.models.common import UUIDTimestampMixin


class TwoFactorSecret(UUIDTimestampMixin, Base):
    __tablename__ = "two_factor_secrets"

    id: Mapped[str] = mapped_column(primary_key=True)  # UUIDTimestampMixin provides this
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(default=False)

    user = relationship("User", back_populates="two_factor_secret")
