"""budgets table

Revision ID: 20260410_0006
Revises: 20260403_0005
Create Date: 2026-04-10 16:25:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260410_0006"
down_revision = "20260403_0005"
branch_labels = None
depends_on = None

budget_period = postgresql.ENUM("monthly", "weekly", "yearly", name="budget_period", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    budget_period.create(bind, checkfirst=True)

    op.create_table(
        "budgets",
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount_limit", sa.Numeric(14, 2), nullable=False),
        sa.Column("period", budget_period, nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("budgets")
    bind = op.get_bind()
    budget_period.drop(bind, checkfirst=True)
