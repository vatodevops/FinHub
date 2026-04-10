"""bank connections

Revision ID: 20260403_0004
Revises: 20260403_0003
Create Date: 2026-04-03 19:52:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260403_0004"
down_revision = "20260403_0003"
branch_labels = None
depends_on = None

bank_connection_status = postgresql.ENUM("pending", "linked", "expired", "failed", name="bank_connection_status", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    bank_connection_status.create(bind, checkfirst=True)
    op.create_table(
        "bank_connections",
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("provider", sa.String(length=100), nullable=False),
        sa.Column("requisition_id", sa.String(length=255), nullable=False),
        sa.Column("reference", sa.String(length=255), nullable=False),
        sa.Column("institution_external_id", sa.String(length=255), nullable=True),
        sa.Column("institution_name", sa.String(length=255), nullable=True),
        sa.Column("link", sa.Text(), nullable=True),
        sa.Column("status", bank_connection_status, nullable=False),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("requisition_id"),
    )


def downgrade() -> None:
    op.drop_table("bank_connections")
    bind = op.get_bind()
    bank_connection_status.drop(bind, checkfirst=True)
