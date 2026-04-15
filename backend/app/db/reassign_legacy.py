"""Reasigna todos los datos de un user placeholder (por defecto legacy@finhub.local)
al user real indicado por email. Pensado para ejecutar una sola vez tras la migración
20260415_0009 en producción.

Uso:
    python -m app.db.reassign_legacy --target me@example.com
    python -m app.db.reassign_legacy --target me@example.com --source legacy@finhub.local --dry-run
"""

from __future__ import annotations

import argparse
import sys

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.auth import AuthSession, User
from app.models.bank_connection import BankConnection
from app.models.budget import Budget
from app.models.categories import Category
from app.models.entities import Account, Institution, Transaction, TransactionLink
from app.models.manual import ManualPlannedItem
from app.models.recurring import RecurringOccurrence, RecurringSeries


# Tablas simples (basta con flipar user_id).
SIMPLE_TABLES = [
    Institution,
    Account,
    Transaction,
    TransactionLink,
    Budget,
    BankConnection,
    ManualPlannedItem,
    RecurringSeries,
    RecurringOccurrence,
]


def _merge_categories(db: Session, source_id, target_id) -> dict:
    """Une categorías por slug. Devuelve mapping source_cat_id -> target_cat_id para las fusionadas."""
    source_cats = db.scalars(select(Category).where(Category.user_id == source_id)).all()
    target_cats = db.scalars(select(Category).where(Category.user_id == target_id)).all()
    target_by_slug = {c.slug: c for c in target_cats}

    merges: dict = {}
    moves: list[Category] = []
    for cat in source_cats:
        twin = target_by_slug.get(cat.slug)
        if twin:
            merges[cat.id] = twin.id
        else:
            moves.append(cat)
    return {"merges": merges, "moves": moves}


def _apply_category_merges(db: Session, merges: dict) -> int:
    """Redirige transactions.category_id y budgets.category_id a la categoría del destino."""
    touched = 0
    for src_id, dst_id in merges.items():
        touched += db.execute(
            update(Transaction).where(Transaction.category_id == src_id).values(category_id=dst_id)
        ).rowcount or 0
        touched += db.execute(
            update(Budget).where(Budget.category_id == src_id).values(category_id=dst_id)
        ).rowcount or 0
    return touched


def reassign(source_email: str, target_email: str, dry_run: bool) -> int:
    db: Session = SessionLocal()
    try:
        source = db.scalar(select(User).where(User.email == source_email.lower()))
        if not source:
            print(f"[!] No encuentro el user origen {source_email}", file=sys.stderr)
            return 1

        target = db.scalar(select(User).where(User.email == target_email.lower()))
        if not target:
            print(f"[!] No encuentro el user destino {target_email}", file=sys.stderr)
            return 1

        if source.id == target.id:
            print("[!] Origen y destino son el mismo user", file=sys.stderr)
            return 1

        print(f"Origen:  {source.email} ({source.id})")
        print(f"Destino: {target.email} ({target.id})")

        cat_plan = _merge_categories(db, source.id, target.id)
        print(f"Categorías a fusionar por slug: {len(cat_plan['merges'])}")
        print(f"Categorías a trasladar tal cual: {len(cat_plan['moves'])}")

        for model in SIMPLE_TABLES:
            count = db.scalar(
                select(model.__table__.c.user_id).where(model.user_id == source.id).limit(1)
            )
            total = db.query(model).filter(model.user_id == source.id).count()
            print(f"  {model.__tablename__}: {total} filas")

        if dry_run:
            print("[dry-run] no se toca nada")
            return 0

        moved_refs = _apply_category_merges(db, cat_plan["merges"])
        print(f"Category refs redirigidas: {moved_refs}")

        for cat_id in cat_plan["merges"].keys():
            db.execute(delete(Category).where(Category.id == cat_id))

        for cat in cat_plan["moves"]:
            cat.user_id = target.id

        for model in SIMPLE_TABLES:
            db.execute(
                update(model.__table__)
                .where(model.__table__.c.user_id == source.id)
                .values(user_id=target.id)
            )

        db.execute(delete(AuthSession).where(AuthSession.user_id == source.id))
        db.execute(delete(User).where(User.id == source.id))
        db.commit()
        print("[ok] reasignación completada")
        return 0
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="legacy@finhub.local")
    parser.add_argument("--target", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    return reassign(args.source, args.target, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
