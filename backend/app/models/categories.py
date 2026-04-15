from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin


class Category(UUIDTimestampMixin, Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("user_id", "slug", name="uq_category_user_slug"),
        UniqueConstraint("user_id", "name", name="uq_category_user_name"),
    )

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(20))
    icon: Mapped[str | None] = mapped_column(String(50))
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"))

    parent = relationship("Category", remote_side="Category.id", backref="children")
    transactions = relationship("Transaction", back_populates="category")
