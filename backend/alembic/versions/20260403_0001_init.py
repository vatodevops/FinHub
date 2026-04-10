"""initial schema

Revision ID: 20260403_0001
Revises: 
Create Date: 2026-04-03 19:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260403_0001"
down_revision = None
branch_labels = None
depends_on = None


source_type = postgresql.ENUM("bank", "curve", "broker", name="source_type", create_type=False)
transaction_source_type = postgresql.ENUM("bank", "curve", "broker", name="transaction_source_type", create_type=False)
account_kind = postgresql.ENUM("checking", "savings", "credit_card", "investment", "cash", name="account_kind", create_type=False)
transaction_channel = postgresql.ENUM(
    "card", "transfer", "direct_debit", "cash", "fee", "income", "other", name="transaction_channel", create_type=False
)
transaction_status = postgresql.ENUM("booked", "pending", "shadow", "duplicate", name="transaction_status", create_type=False)
link_type = postgresql.ENUM("curve_settlement", "duplicate", "transfer_pair", name="link_type", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    source_type.create(bind, checkfirst=True)
    transaction_source_type.create(bind, checkfirst=True)
    account_kind.create(bind, checkfirst=True)
    transaction_channel.create(bind, checkfirst=True)
    transaction_status.create(bind, checkfirst=True)
    link_type.create(bind, checkfirst=True)

    op.create_table(
        "institutions",
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("source_type", source_type, nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "accounts",
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("iban_masked", sa.String(length=64), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("kind", account_kind, nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("institution_id", "external_id", name="uq_account_institution_external"),
    )

    op.create_table(
        "transactions",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_type", transaction_source_type, nullable=False),
        sa.Column("source_id", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("booked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("value_date", sa.Date(), nullable=True),
        sa.Column("merchant_raw", sa.String(length=255), nullable=True),
        sa.Column("merchant_clean", sa.String(length=255), nullable=True),
        sa.Column("description_raw", sa.Text(), nullable=True),
        sa.Column("channel", transaction_channel, nullable=False),
        sa.Column("status", transaction_status, nullable=False),
        sa.Column("fingerprint", sa.String(length=255), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_type", "source_id", name="uq_transaction_source"),
    )
    op.create_index(op.f("ix_transactions_fingerprint"), "transactions", ["fingerprint"], unique=False)

    op.create_table(
        "transaction_links",
        sa.Column("left_transaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("right_transaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("link_type", link_type, nullable=False),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["left_transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["right_transaction_id"], ["transactions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("transaction_links")
    op.drop_index(op.f("ix_transactions_fingerprint"), table_name="transactions")
    op.drop_table("transactions")
    op.drop_table("accounts")
    op.drop_table("institutions")

    bind = op.get_bind()
    link_type.drop(bind, checkfirst=True)
    transaction_status.drop(bind, checkfirst=True)
    transaction_channel.drop(bind, checkfirst=True)
    account_kind.drop(bind, checkfirst=True)
    transaction_source_type.drop(bind, checkfirst=True)
    source_type.drop(bind, checkfirst=True)
