"""session metadata: user_agent, ip_address

Revision ID: 20260415_0011
Revises: 20260415_0010
Create Date: 2026-04-15 13:30:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260415_0011"
down_revision = "20260415_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("auth_sessions", sa.Column("user_agent", sa.String(length=500), nullable=True))
    op.add_column("auth_sessions", sa.Column("ip_address", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("auth_sessions", "ip_address")
    op.drop_column("auth_sessions", "user_agent")
