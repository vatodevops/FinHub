"""recurring series and occurrences

Revision ID: 20260403_0002
Revises: 20260403_0001
Create Date: 2026-04-03 19:40:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260403_0002"
down_revision = "20260403_0001"
branch_labels = None
depends_on = None

recurrence_type = postgresql.ENUM(
    "weekly", "monthly", "bimonthly", "quarterly", "yearly", "irregular", name="recurrence_type", create_type=False
)
recurrence_state = postgresql.ENUM(
    "auto_detected", "manual_confirmed", "manual_ignored", "inactive", name="recurrence_state", create_type=False
)
occurrence_status = postgresql.ENUM("expected", "due", "paid", "missed", "skipped", name="occurrence_status", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    recurrence_type.create(bind, checkfirst=True)
    recurrence_state.create(bind, checkfirst=True)
    occurrence_status.create(bind, checkfirst=True)

    op.create_table(
        "recurring_series",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("merchant_clean", sa.String(length=255), nullable=True),
        sa.Column("channel", sa.String(length=50), nullable=True),
        sa.Column("recurrence_type", recurrence_type, nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=True),
        sa.Column("typical_day_of_month", sa.Integer(), nullable=True),
        sa.Column("amount_mean", sa.Numeric(14, 2), nullable=True),
        sa.Column("amount_deviation", sa.Numeric(14, 2), nullable=True),
        sa.Column("next_expected_date", sa.Date(), nullable=True),
        sa.Column("confidence", sa.Numeric(5, 2), nullable=True),
        sa.Column("state", recurrence_state, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "recurring_occurrences",
        sa.Column("series_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expected_date", sa.Date(), nullable=False),
        sa.Column("expected_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("matched_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", occurrence_status, nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["matched_transaction_id"], ["transactions.id"]),
        sa.ForeignKeyConstraint(["series_id"], ["recurring_series.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("recurring_occurrences")
    op.drop_table("recurring_series")

    bind = op.get_bind()
    occurrence_status.drop(bind, checkfirst=True)
    recurrence_state.drop(bind, checkfirst=True)
    recurrence_type.drop(bind, checkfirst=True)
