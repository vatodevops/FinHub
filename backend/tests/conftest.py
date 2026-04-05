import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.categories import Category
from app.models import *  # noqa: F401,F403
from app.models.entities import (
    Account,
    AccountKind,
    Institution,
    SourceType,
    Transaction,
    TransactionChannel,
    TransactionStatus,
)


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db):
    def _override():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def seed_data(db):
    institution = Institution(
        id=uuid.uuid4(),
        name="Test Bank",
        provider="test",
        source_type=SourceType.bank,
    )
    db.add(institution)
    db.flush()

    account = Account(
        id=uuid.uuid4(),
        institution_id=institution.id,
        name="Test Checking",
        currency="EUR",
        kind=AccountKind.checking,
    )
    db.add(account)
    db.flush()

    category = Category(
        id=uuid.uuid4(),
        name="Supermercado",
        slug="supermercado",
        color="#22c55e",
    )
    db.add(category)
    db.flush()

    tx = Transaction(
        id=uuid.uuid4(),
        account_id=account.id,
        source_type=SourceType.bank,
        source_id="test-tx-001",
        amount=Decimal("-42.50"),
        currency="EUR",
        booked_at=datetime.now(timezone.utc),
        merchant_raw="MERCADONA",
        merchant_clean="Mercadona",
        channel=TransactionChannel.card,
        status=TransactionStatus.booked,
    )
    db.add(tx)
    db.commit()

    return {"institution": institution, "account": account, "category": category, "transaction": tx}
