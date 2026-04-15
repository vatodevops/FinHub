"""extend user profile with picture, locale, email_verified, auth_provider, last_login_at

Revision ID: 20260415_0010
Revises: 20260415_0009
Create Date: 2026-04-15 13:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260415_0010"
down_revision = "20260415_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("users", sa.Column("picture_url", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("locale", sa.String(length=16), nullable=True))
    op.add_column("users", sa.Column("auth_provider", sa.String(length=20), nullable=False, server_default="local"))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))

    bind = op.get_bind()
    bind.execute(sa.text("UPDATE users SET auth_provider = 'google' WHERE google_sub IS NOT NULL"))
    bind.execute(sa.text("UPDATE users SET email_verified = TRUE WHERE google_sub IS NOT NULL"))

    op.alter_column("users", "password_hash", existing_type=sa.Text(), nullable=True)


def downgrade() -> None:
    op.alter_column("users", "password_hash", existing_type=sa.Text(), nullable=False)
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "auth_provider")
    op.drop_column("users", "locale")
    op.drop_column("users", "picture_url")
    op.drop_column("users", "email_verified")
