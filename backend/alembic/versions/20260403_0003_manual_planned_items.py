"""manual planned items

Revision ID: 20260403_0003
Revises: 20260403_0002
Create Date: 2026-04-03 19:48:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260403_0003"
down_revision = "20260403_0002"
branch_labels = None
depends_on = None

manual_item_kind = sa.Enum("one_off", "recurring", name="manual_item_kind")
manual_item_status = sa.Enum("planned", "paid", "skipped", "cancelled", name="manual_item_status")


def upgrade() -> None:
    bind = op.get_bind()
    manual_item_kind.create(bind, checkfirst=True)
    manual_item_status.create(bind, checkfirst=True)

    op.create_table(
        "manual_planned_items",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("merchant_hint", sa.String(length=255), nullable=True),
        sa.Column("kind", manual_item_kind, nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("expected_date", sa.Date(), nullable=True),
        sa.Column("recurrence_rule", sa.String(length=100), nullable=True),
        sa.Column("status", manual_item_status, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("manual_planned_items")

    bind = op.get_bind()
    manual_item_status.drop(bind, checkfirst=True)
    manual_item_kind.drop(bind, checkfirst=True)
