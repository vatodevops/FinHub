import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps.auth import require_auth
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.auth import User
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
def test_user(db):
    user = User(
        id=uuid.uuid4(),
        email="tester@finhub.local",
        full_name="Tester",
        password_hash=hash_password("tester1234"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture()
def client(db, test_user):
    def _override_db():
        try:
            yield db
        finally:
            pass

    def _override_auth():
        return test_user

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[require_auth] = _override_auth
    with TestClient(app, base_url="http://localhost:3001") as c:
        c.headers.update({"origin": "http://localhost:3001"})
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def seed_data(db, test_user):
    institution = Institution(
        id=uuid.uuid4(),
        user_id=test_user.id,
        name="Test Bank",
        provider="test",
        source_type=SourceType.bank,
    )
    db.add(institution)
    db.flush()

    account = Account(
        id=uuid.uuid4(),
        user_id=test_user.id,
        institution_id=institution.id,
        name="Test Checking",
        currency="EUR",
        kind=AccountKind.checking,
    )
    db.add(account)
    db.flush()

    category = Category(
        id=uuid.uuid4(),
        user_id=test_user.id,
        name="Supermercado",
        slug="supermercado",
        color="#22c55e",
    )
    db.add(category)
    db.flush()

    tx = Transaction(
        id=uuid.uuid4(),
        user_id=test_user.id,
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

    return {
        "user": test_user,
        "institution": institution,
        "account": account,
        "category": category,
        "transaction": tx,
    }
