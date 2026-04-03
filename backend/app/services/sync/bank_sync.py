from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.bank_connection import BankConnection, BankConnectionStatus
from app.models.entities import Account, AccountKind, Institution, SourceType, Transaction, TransactionStatus
from app.services.connectors.banks.gocardless import GoCardlessBankConnector


async def sync_bank_connection(db: Session, connection: BankConnection) -> dict:
    connector = GoCardlessBankConnector()
    requisition = await connector.client.get_requisition(connection.requisition_id)
    connection.link = requisition.get("link")
    accounts = await connector.list_accounts(connection.requisition_id)

    institution = _ensure_institution(db, connection, requisition)
    created_accounts = 0
    upserted_transactions = 0

    for normalized_account in accounts:
        account = (
            db.query(Account)
            .filter(Account.institution_id == institution.id)
            .filter(Account.external_id == normalized_account.external_id)
            .one_or_none()
        )
        if account is None:
            account = Account(
                institution_id=institution.id,
                name=normalized_account.name,
                iban_masked=normalized_account.iban_masked,
                currency=normalized_account.currency,
                kind=AccountKind.checking,
                external_id=normalized_account.external_id,
                is_active=True,
            )
            db.add(account)
            db.flush()
            created_accounts += 1

        txs = await connector.list_transactions(
            connection.requisition_id,
            normalized_account.external_id,
            from_date=(datetime.now(UTC) - timedelta(days=120)).date(),
        )
        for tx in txs:
            row = (
                db.query(Transaction)
                .filter(Transaction.source_type == SourceType.bank)
                .filter(Transaction.source_id == tx.source_id)
                .one_or_none()
            )
            if row is None:
                row = Transaction(
                    account_id=account.id,
                    source_type=SourceType.bank,
                    source_id=tx.source_id,
                    amount=tx.amount,
                    currency=tx.currency,
                    booked_at=tx.booked_at,
                    value_date=tx.value_date,
                    merchant_raw=tx.merchant_raw,
                    merchant_clean=tx.merchant_raw,
                    description_raw=tx.description_raw,
                    channel=tx.channel,
                    status=TransactionStatus.booked,
                )
                db.add(row)
            else:
                row.account_id = account.id
                row.amount = tx.amount
                row.currency = tx.currency
                row.booked_at = tx.booked_at
                row.value_date = tx.value_date
                row.merchant_raw = tx.merchant_raw
                row.merchant_clean = tx.merchant_raw
                row.description_raw = tx.description_raw
                row.channel = tx.channel
            upserted_transactions += 1

    connection.status = BankConnectionStatus.linked
    connection.last_synced_at = datetime.now(UTC)
    connection.error_message = None
    db.commit()
    db.refresh(connection)
    return {
        "connection_id": str(connection.id),
        "accounts_seen": len(accounts),
        "accounts_created": created_accounts,
        "transactions_upserted": upserted_transactions,
        "status": connection.status.value,
    }


def _ensure_institution(db: Session, connection: BankConnection, requisition: dict) -> Institution:
    institution = None
    if connection.institution_id:
        institution = db.query(Institution).filter(Institution.id == connection.institution_id).one_or_none()
    if institution is None:
        external_id = connection.institution_external_id or requisition.get("institution_id")
        institution = (
            db.query(Institution)
            .filter(Institution.provider == connection.provider)
            .filter(Institution.external_id == external_id)
            .one_or_none()
        )
    if institution is None:
        institution = Institution(
            name=connection.institution_name or requisition.get("institution_id") or "Bank",
            provider=connection.provider,
            external_id=connection.institution_external_id or requisition.get("institution_id"),
            source_type=SourceType.bank,
        )
        db.add(institution)
        db.flush()
    connection.institution_id = institution.id
    return institution
