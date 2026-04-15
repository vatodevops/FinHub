"""scope all domain tables by user_id

Revision ID: 20260415_0009
Revises: 20260410_0008
Create Date: 2026-04-15 12:00:00
"""

import hashlib
import secrets
import uuid

from alembic import op
import sqlalchemy as sa


revision = "20260415_0009"
down_revision = "20260410_0008"
branch_labels = None
depends_on = None


SCOPED_TABLES = [
    "institutions",
    "accounts",
    "transactions",
    "transaction_links",
    "categories",
    "budgets",
    "bank_connections",
    "manual_planned_items",
    "recurring_series",
    "recurring_occurrences",
]


def _ensure_default_user(bind) -> str:
    users = sa.table(
        "users",
        sa.column("id", sa.Uuid()),
        sa.column("email", sa.String()),
        sa.column("full_name", sa.String()),
        sa.column("password_hash", sa.Text()),
        sa.column("is_active", sa.Boolean()),
    )
    existing = bind.execute(sa.select(users.c.id).order_by(users.c.email).limit(1)).scalar()
    if existing:
        return str(existing)

    new_id = uuid.uuid4()
    placeholder_hash = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
    bind.execute(
        users.insert().values(
            id=new_id,
            email="legacy@finhub.local",
            full_name="Legacy data owner",
            password_hash=placeholder_hash,
            is_active=True,
        )
    )
    return str(new_id)


def upgrade() -> None:
    bind = op.get_bind()

    for table in SCOPED_TABLES:
        op.add_column(table, sa.Column("user_id", sa.Uuid(), nullable=True))

    owner_id = _ensure_default_user(bind)

    for table in SCOPED_TABLES:
        bind.execute(sa.text(f"UPDATE {table} SET user_id = :uid WHERE user_id IS NULL"), {"uid": owner_id})

    for table in SCOPED_TABLES:
        op.alter_column(table, "user_id", existing_type=sa.Uuid(), nullable=False)
        op.create_foreign_key(
            f"fk_{table}_user_id_users",
            table,
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.create_index(f"ix_{table}_user_id", table, ["user_id"], unique=False)

    op.drop_constraint("uq_transaction_source", "transactions", type_="unique")
    op.create_unique_constraint(
        "uq_transaction_user_source", "transactions", ["user_id", "source_type", "source_id"]
    )

    op.drop_constraint("categories_name_key", "categories", type_="unique")
    op.drop_constraint("categories_slug_key", "categories", type_="unique")
    op.create_unique_constraint("uq_category_user_slug", "categories", ["user_id", "slug"])
    op.create_unique_constraint("uq_category_user_name", "categories", ["user_id", "name"])


def downgrade() -> None:
    op.drop_constraint("uq_category_user_name", "categories", type_="unique")
    op.drop_constraint("uq_category_user_slug", "categories", type_="unique")
    op.create_unique_constraint("categories_slug_key", "categories", ["slug"])
    op.create_unique_constraint("categories_name_key", "categories", ["name"])

    op.drop_constraint("uq_transaction_user_source", "transactions", type_="unique")
    op.create_unique_constraint("uq_transaction_source", "transactions", ["source_type", "source_id"])

    for table in SCOPED_TABLES:
        op.drop_index(f"ix_{table}_user_id", table_name=table)
        op.drop_constraint(f"fk_{table}_user_id_users", table, type_="foreignkey")
        op.drop_column(table, "user_id")
