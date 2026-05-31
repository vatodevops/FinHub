import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.common import UUIDTimestampMixin


class SourceType(str, enum.Enum):
    bank = "bank"
    curve = "curve"
    broker = "broker"


class AccountKind(str, enum.Enum):
    checking = "checking"
    savings = "savings"
    credit_card = "credit_card"
    investment = "investment"
    cash = "cash"


class TransactionChannel(str, enum.Enum):
    card = "card"
    transfer = "transfer"
    direct_debit = "direct_debit"
    cash = "cash"
    fee = "fee"
    income = "income"
    other = "other"


class TransactionStatus(str, enum.Enum):
    booked = "booked"
    pending = "pending"
    shadow = "shadow"
    duplicate = "duplicate"


class LinkType(str, enum.Enum):
    curve_settlement = "curve_settlement"
    duplicate = "duplicate"
    transfer_pair = "transfer_pair"


class Institution(UUIDTimestampMixin, Base):
    __tablename__ = "institutions"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType, name="source_type"), nullable=False)

    accounts: Mapped[list["Account"]] = relationship(back_populates="institution")


class Account(UUIDTimestampMixin, Base):
    __tablename__ = "accounts"
    __table_args__ = (UniqueConstraint("institution_id", "external_id", name="uq_account_institution_external"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_id: Mapped[str] = mapped_column(ForeignKey("institutions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    iban_masked: Mapped[str | None] = mapped_column(String(64))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    kind: Mapped[AccountKind] = mapped_column(Enum(AccountKind, name="account_kind"), nullable=False)
    external_id: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)

    institution: Mapped[Institution] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account")


class Transaction(UUIDTimestampMixin, Base):
    __tablename__ = "transactions"
    __table_args__ = (UniqueConstraint("user_id", "source_type", "source_id", name="uq_transaction_user_source"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"))
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType, name="transaction_source_type"), nullable=False)
    source_id: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="EUR")
    booked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    value_date: Mapped[date | None] = mapped_column(Date)
    merchant_raw: Mapped[str | None] = mapped_column(String(255))
    merchant_clean: Mapped[str | None] = mapped_column(String(255))
    description_raw: Mapped[str | None] = mapped_column(Text)
    channel: Mapped[TransactionChannel] = mapped_column(Enum(TransactionChannel, name="transaction_channel"), nullable=False)
    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus, name="transaction_status"), nullable=False, default=TransactionStatus.booked
    )
    fingerprint: Mapped[str | None] = mapped_column(String(255), index=True)

    account: Mapped[Account] = relationship(back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    outgoing_links: Mapped[list["TransactionLink"]] = relationship(
        back_populates="left_transaction", foreign_keys="TransactionLink.left_transaction_id"
    )
    incoming_links: Mapped[list["TransactionLink"]] = relationship(
        back_populates="right_transaction", foreign_keys="TransactionLink.right_transaction_id"
    )
    splits: Mapped[list["TransactionSplit"]] = relationship(
        back_populates="transaction", cascade="all, delete-orphan"
    )


class TransactionLink(UUIDTimestampMixin, Base):
    __tablename__ = "transaction_links"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    left_transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), nullable=False)
    right_transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), nullable=False)
    link_type: Mapped[LinkType] = mapped_column(Enum(LinkType, name="link_type"), nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    notes: Mapped[str | None] = mapped_column(Text)

    left_transaction: Mapped[Transaction] = relationship(
        back_populates="outgoing_links", foreign_keys=[left_transaction_id]
    )
    right_transaction: Mapped[Transaction] = relationship(
        back_populates="incoming_links", foreign_keys=[right_transaction_id]
    )
