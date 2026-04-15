"""add google oauth support

Revision ID: 20260410_0008
Revises: 20260410_0007
Create Date: 2026-04-10 17:30:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260410_0008"
down_revision = "20260410_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("google_sub", sa.String(length=255), nullable=True))
    op.create_index(op.f("ix_users_google_sub"), "users", ["google_sub"], unique=False)
    op.create_unique_constraint("uq_users_google_sub", "users", ["google_sub"])


def downgrade() -> None:
    op.drop_constraint("uq_users_google_sub", "users", type_="unique")
    op.drop_index(op.f("ix_users_google_sub"), table_name="users")
    op.drop_column("users", "google_sub")
