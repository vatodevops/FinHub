from datetime import UTC, date, datetime
from decimal import Decimal

from app.db.base import Base
from app.db.session import SessionLocal, engine
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


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Institution).count() > 0:
            return

        groceries = Category(name="Supermercado", slug="supermercado", color="#56d364")
        subscriptions = Category(name="Suscripciones", slug="suscripciones", color="#6ea8fe")
        transfers = Category(name="Transferencias", slug="transferencias", color="#9fb0d1")
        shopping = Category(name="Compras", slug="compras", color="#ffb86b")
        db.add_all([groceries, subscriptions, transfers, shopping])
        db.flush()

        curve = Institution(name="Curve", provider="manual", source_type=SourceType.curve)
        bbva = Institution(name="BBVA", provider="manual", source_type=SourceType.bank)
        db.add_all([curve, bbva])
        db.flush()

        curve_account = Account(
            institution_id=curve.id,
            name="Curve Main",
            currency="EUR",
            kind=AccountKind.credit_card,
            external_id="curve-main",
            is_active=True,
        )
        bbva_account = Account(
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
            account_id=curve_account.id,
            category_id=shopping.id,
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
            account_id=bbva_account.id,
            category_id=shopping.id,
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
                series_id=internet.id,
                expected_date=date(now.year, now.month, 3),
                expected_amount=Decimal("52.30"),
                status=OccurrenceStatus.expected,
            )
        )

        db.add(
            ManualPlannedItem(
                account_id=None,
                name="Peluquería",
                merchant_hint="Peluquería barrio",
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
