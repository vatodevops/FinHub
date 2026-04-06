import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.entities import (
    Account,
    AccountKind,
    Institution,
    SourceType,
    Transaction,
    TransactionChannel,
    TransactionStatus,
)
from app.schemas.accounts import AccountResponse, CreateAccountRequest, UpdateAccountRequest

router = APIRouter()


def _account_to_response(account: Account, db: Session) -> dict:
    balance = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
        Transaction.account_id == account.id,
        Transaction.status != TransactionStatus.duplicate,
    ).scalar()
    return {
        "id": account.id,
        "institution_id": account.institution_id,
        "name": account.name,
        "iban_masked": account.iban_masked,
        "currency": account.currency,
        "kind": account.kind.value if isinstance(account.kind, AccountKind) else account.kind,
        "is_active": account.is_active,
        "institution_name": account.institution.name if account.institution else None,
        "balance": str(balance),
    }


def _get_or_create_institution(db: Session, name: str) -> Institution:
    institution = db.query(Institution).filter(Institution.name == name).first()
    if not institution:
        institution = Institution(name=name, provider="manual", source_type=SourceType.bank)
        db.add(institution)
        db.flush()
    return institution


@router.get("/accounts", response_model=list[AccountResponse])
def list_accounts(db: Session = Depends(get_db)) -> list[AccountResponse]:
    accounts = db.query(Account).order_by(Account.name.asc()).all()
    return [_account_to_response(a, db) for a in accounts]


@router.post("/accounts", response_model=AccountResponse, status_code=201)
def create_account(payload: CreateAccountRequest, db: Session = Depends(get_db)) -> AccountResponse:
    try:
        kind = AccountKind(payload.kind)
    except ValueError:
        valid = [k.value for k in AccountKind]
        raise HTTPException(status_code=422, detail=f"Tipo invalido. Valores permitidos: {valid}")

    institution = _get_or_create_institution(db, payload.institution_name or "Manual")

    account = Account(
        institution_id=institution.id,
        name=payload.name,
        kind=kind,
        currency=payload.currency,
        iban_masked=payload.iban,
        is_active=True,
    )
    db.add(account)
    db.flush()

    if payload.initial_balance != Decimal("0.00"):
        initial_tx = Transaction(
            account_id=account.id,
            source_type=SourceType.bank,
            source_id=f"initial-{account.id}",
            amount=payload.initial_balance,
            currency=payload.currency,
            channel=TransactionChannel.other,
            status=TransactionStatus.booked,
            merchant_clean="Saldo inicial",
            description_raw="Saldo inicial de la cuenta",
        )
        db.add(initial_tx)

    db.commit()
    db.refresh(account)
    return _account_to_response(account, db)


@router.patch("/accounts/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: uuid.UUID,
    payload: UpdateAccountRequest,
    db: Session = Depends(get_db),
) -> AccountResponse:
    account = db.query(Account).filter(Account.id == account_id).one_or_none()
    if not account:
        raise NotFoundError("account_not_found")

    if payload.name is not None:
        account.name = payload.name
    if payload.kind is not None:
        try:
            account.kind = AccountKind(payload.kind)
        except ValueError:
            raise HTTPException(status_code=422, detail="Tipo invalido")
    if payload.currency is not None:
        account.currency = payload.currency
    if payload.iban is not None:
        account.iban_masked = payload.iban
    if payload.is_active is not None:
        account.is_active = payload.is_active
    if payload.institution_name is not None:
        institution = _get_or_create_institution(db, payload.institution_name)
        account.institution_id = institution.id

    db.commit()
    db.refresh(account)
    return _account_to_response(account, db)


@router.delete("/accounts/{account_id}", status_code=204)
def delete_account(account_id: uuid.UUID, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).one_or_none()
    if not account:
        raise NotFoundError("account_not_found")
    db.query(Transaction).filter(Transaction.account_id == account_id).delete()
    db.delete(account)
    db.commit()
