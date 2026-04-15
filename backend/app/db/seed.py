from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.auth import User
from app.models.categories import Category
from app.models.entities import (
    Account,
    AccountKind,
    Institution,
    SourceType,
    Transaction,
    TransactionChannel,
    TransactionStatus,
)
from app.models.manual import ManualItemKind, ManualItemStatus, ManualPlannedItem
from app.models.recurring import (
    OccurrenceStatus,
    RecurrenceState,
    RecurrenceType,
    RecurringOccurrence,
    RecurringSeries,
)

DEFAULT_CATEGORIES = [
    ("Alimentacion", "alimentacion", "#56d364", "shopping-cart"),
    ("Restaurantes", "restaurantes", "#ff9f43", "utensils"),
    ("Transporte", "transporte", "#6ea8fe", "car"),
    ("Hogar", "hogar", "#a78bfa", "home"),
    ("Suministros", "suministros", "#f59e0b", "zap"),
    ("Salud", "salud", "#ef4444", "heart"),
    ("Ocio", "ocio", "#ec4899", "gamepad"),
    ("Ropa", "ropa", "#8b5cf6", "shirt"),
    ("Educacion", "educacion", "#14b8a6", "book"),
    ("Suscripciones", "suscripciones", "#6ea8fe", "repeat"),
    ("Seguros", "seguros", "#64748b", "shield"),
    ("Mascotas", "mascotas", "#f97316", "paw-print"),
    ("Regalos", "regalos", "#e879f9", "gift"),
    ("Viajes", "viajes", "#22d3ee", "plane"),
    ("Compras", "compras", "#ffb86b", "shopping-bag"),
    ("Transferencias", "transferencias", "#9fb0d1", "arrow-left-right"),
    ("Nomina", "nomina", "#22c55e", "briefcase"),
    ("Otros ingresos", "otros-ingresos", "#10b981", "plus-circle"),
    ("Impuestos", "impuestos", "#ef4444", "file-text"),
    ("Otros gastos", "otros-gastos", "#94a3b8", "more-horizontal"),
]


def seed_default_categories(db: Session, user_id) -> None:
    existing_slugs = {
        c.slug
        for c in db.query(Category).filter(Category.user_id == user_id).all()
    }
    for name, slug, color, icon in DEFAULT_CATEGORIES:
        if slug in existing_slugs:
            continue
        db.add(Category(user_id=user_id, name=name, slug=slug, color=color, icon=icon))
    db.flush()


def seed() -> None:
    if str(engine.url).startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        demo = db.query(User).filter(User.email == "demo@finhub.local").one_or_none()
        if demo is None:
            demo = User(
                email="demo@finhub.local",
                full_name="Demo",
                password_hash=hash_password("demo1234"),
                is_active=True,
            )
            db.add(demo)
            db.flush()

        seed_default_categories(db, demo.id)

        if db.query(Institution).filter(Institution.user_id == demo.id).count() > 0:
            db.commit()
            return

        curve = Institution(user_id=demo.id, name="Curve", provider="manual", source_type=SourceType.curve)
        bbva = Institution(user_id=demo.id, name="BBVA", provider="manual", source_type=SourceType.bank)
        db.add_all([curve, bbva])
        db.flush()

        shopping = (
            db.query(Category)
            .filter(Category.user_id == demo.id, Category.slug == "compras")
            .first()
        )

        curve_account = Account(
            user_id=demo.id,
            institution_id=curve.id,
            name="Curve Main",
            currency="EUR",
            kind=AccountKind.credit_card,
            external_id="curve-main",
            is_active=True,
        )
        bbva_account = Account(
            user_id=demo.id,
            institution_id=bbva.id,
            name="BBVA Cuenta",
            currency="EUR",
            kind=AccountKind.checking,
            external_id="bbva-main",
            iban_masked="ES**1234",
            is_active=True,
        )
        db.add_all([curve_account, bbva_account])
        db.flush()

        now = datetime.now(UTC)
        curve_tx = Transaction(
            user_id=demo.id,
            account_id=curve_account.id,
            category_id=shopping.id if shopping else None,
            source_type=SourceType.curve,
            source_id="curve-tx-1",
            amount=Decimal("12.34"),
            currency="EUR",
            booked_at=now,
            merchant_raw="Amazon",
            merchant_clean="Amazon",
            description_raw="Amazon purchase via Curve",
            channel=TransactionChannel.card,
            status=TransactionStatus.booked,
        )
        bank_tx = Transaction(
            user_id=demo.id,
            account_id=bbva_account.id,
            category_id=shopping.id if shopping else None,
            source_type=SourceType.bank,
            source_id="bbva-tx-1",
            amount=Decimal("12.34"),
            currency="EUR",
            booked_at=now,
            merchant_raw="CRV-9283 AMAZON",
            merchant_clean="Amazon",
            description_raw="CRV-9283 AMAZON",
            channel=TransactionChannel.card,
            status=TransactionStatus.shadow,
        )
        db.add_all([curve_tx, bank_tx])
        db.flush()

        internet = RecurringSeries(
            user_id=demo.id,
            account_id=bbva_account.id,
            name="Internet",
            merchant_clean="Movistar",
            channel="direct_debit",
            recurrence_type=RecurrenceType.monthly,
            interval_days=30,
            typical_day_of_month=3,
            amount_mean=Decimal("52.30"),
            amount_deviation=Decimal("0.00"),
            next_expected_date=date(now.year, now.month, 3),
            confidence=Decimal("0.95"),
            state=RecurrenceState.manual_confirmed,
        )
        db.add(internet)
        db.flush()
        db.add(
            RecurringOccurrence(
                user_id=demo.id,
                series_id=internet.id,
                expected_date=date(now.year, now.month, 3),
                expected_amount=Decimal("52.30"),
                status=OccurrenceStatus.expected,
            )
        )

        db.add(
            ManualPlannedItem(
                user_id=demo.id,
                account_id=None,
                name="Peluqueria",
                merchant_hint="Peluqueria barrio",
                kind=ManualItemKind.recurring,
                amount=Decimal("18.00"),
                currency="EUR",
                expected_date=date(now.year, now.month, min(20, now.day)),
                recurrence_rule="every_4_weeks",
                status=ManualItemStatus.planned,
                notes="Gasto manual, a veces en efectivo",
            )
        )
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
