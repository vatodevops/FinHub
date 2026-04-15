import uuid
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.auth import User
from app.models.entities import (
    Account,
    LinkType,
    SourceType,
    Transaction,
    TransactionChannel,
    TransactionLink,
    TransactionStatus,
)
from app.models.categories import Category
from app.schemas.categories import CategoryResponse, TransactionCategoryUpdate, CreateCategoryRequest, UpdateCategoryRequest
from app.schemas.duplicates import CurveDuplicateCandidateResponse
from app.schemas.transactions import (
    CreateTransactionRequest,
    TransactionResponse,
    TransferRequest,
    UpdateTransactionRequest,
    tx_payload,
)
from app.services.duplicates import list_curve_duplicate_candidates

router = APIRouter()


# ── Transactions ─────────────────────────────────────────────

@router.get("/transactions", response_model=list[TransactionResponse])
def list_transactions(
    account_id: uuid.UUID | None = Query(default=None),
    category_id: uuid.UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    min_amount: float | None = Query(default=None),
    max_amount: float | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[TransactionResponse]:
    query = db.query(Transaction).filter(Transaction.user_id == user.id)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if date_from:
        query = query.filter(Transaction.booked_at >= datetime(date_from.year, date_from.month, date_from.day, tzinfo=timezone.utc))
    if date_to:
        query = query.filter(Transaction.booked_at <= datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59, tzinfo=timezone.utc))
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            Transaction.merchant_clean.ilike(pattern)
            | Transaction.merchant_raw.ilike(pattern)
            | Transaction.description_raw.ilike(pattern)
        )
    rows = query.order_by(Transaction.booked_at.desc().nullslast(), Transaction.created_at.desc()).limit(limit).all()
    return [TransactionResponse.model_validate(tx_payload(tx)) for tx in rows]


@router.post("/transactions", response_model=TransactionResponse, status_code=201)
def create_transaction(
    payload: CreateTransactionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> TransactionResponse:
    account = (
        db.query(Account)
        .filter(Account.id == payload.account_id, Account.user_id == user.id)
        .one_or_none()
    )
    if not account:
        raise NotFoundError("account_not_found")

    try:
        channel = TransactionChannel(payload.channel)
    except ValueError:
        channel = TransactionChannel.other

    booked = datetime(payload.booked_at.year, payload.booked_at.month, payload.booked_at.day, tzinfo=timezone.utc) if payload.booked_at else datetime.now(timezone.utc)

    if payload.category_id:
        category = (
            db.query(Category)
            .filter(Category.id == payload.category_id, Category.user_id == user.id)
            .one_or_none()
        )
        if not category:
            raise NotFoundError("category_not_found")

    tx = Transaction(
        user_id=user.id,
        account_id=payload.account_id,
        category_id=payload.category_id,
        source_type=SourceType.bank,
        source_id=f"manual-{uuid.uuid4()}",
        amount=payload.amount,
        currency=payload.currency,
        booked_at=booked,
        merchant_clean=payload.description,
        merchant_raw=payload.description,
        description_raw=payload.description,
        channel=channel,
        status=TransactionStatus.booked,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return TransactionResponse.model_validate(tx_payload(tx))


@router.patch("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: uuid.UUID,
    payload: UpdateTransactionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> TransactionResponse:
    tx = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == user.id)
        .one_or_none()
    )
    if not tx:
        raise NotFoundError("transaction_not_found")

    if payload.amount is not None:
        tx.amount = payload.amount
    if payload.description is not None:
        tx.merchant_clean = payload.description
        tx.merchant_raw = payload.description
        tx.description_raw = payload.description
    if payload.booked_at is not None:
        tx.booked_at = datetime(payload.booked_at.year, payload.booked_at.month, payload.booked_at.day, tzinfo=timezone.utc)
    if payload.category_id is not None:
        category = (
            db.query(Category)
            .filter(Category.id == payload.category_id, Category.user_id == user.id)
            .one_or_none()
        )
        if not category:
            raise NotFoundError("category_not_found")
        tx.category_id = payload.category_id
    if payload.channel is not None:
        try:
            tx.channel = TransactionChannel(payload.channel)
        except ValueError:
            pass

    db.commit()
    db.refresh(tx)
    return TransactionResponse.model_validate(tx_payload(tx))


@router.delete("/transactions/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
):
    tx = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == user.id)
        .one_or_none()
    )
    if not tx:
        raise NotFoundError("transaction_not_found")
    db.query(TransactionLink).filter(
        TransactionLink.user_id == user.id,
        (TransactionLink.left_transaction_id == transaction_id)
        | (TransactionLink.right_transaction_id == transaction_id),
    ).delete(synchronize_session=False)
    db.delete(tx)
    db.commit()


@router.patch("/transactions/{transaction_id}/category", response_model=TransactionResponse)
def update_transaction_category(
    transaction_id: uuid.UUID,
    payload: TransactionCategoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> TransactionResponse:
    tx = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == user.id)
        .one_or_none()
    )
    if tx is None:
        raise NotFoundError("transaction_not_found")
    if payload.category_id is not None:
        category = (
            db.query(Category)
            .filter(Category.id == payload.category_id, Category.user_id == user.id)
            .one_or_none()
        )
        if not category:
            raise NotFoundError("category_not_found")
    tx.category_id = payload.category_id
    db.commit()
    db.refresh(tx)
    return TransactionResponse.model_validate(tx_payload(tx))


@router.post("/transactions/transfer", response_model=list[TransactionResponse], status_code=201)
def create_transfer(
    payload: TransferRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[TransactionResponse]:
    from_acc = (
        db.query(Account)
        .filter(Account.id == payload.from_account_id, Account.user_id == user.id)
        .one_or_none()
    )
    to_acc = (
        db.query(Account)
        .filter(Account.id == payload.to_account_id, Account.user_id == user.id)
        .one_or_none()
    )
    if not from_acc or not to_acc:
        raise NotFoundError("account_not_found")

    booked = datetime(payload.booked_at.year, payload.booked_at.month, payload.booked_at.day, tzinfo=timezone.utc) if payload.booked_at else datetime.now(timezone.utc)
    link_id = str(uuid.uuid4())

    tx_out = Transaction(
        user_id=user.id,
        account_id=payload.from_account_id,
        source_type=SourceType.bank,
        source_id=f"transfer-out-{link_id}",
        amount=-payload.amount,
        currency=payload.currency,
        booked_at=booked,
        merchant_clean=payload.description,
        description_raw=f"Transferencia a {to_acc.name}",
        channel=TransactionChannel.transfer,
        status=TransactionStatus.booked,
    )
    tx_in = Transaction(
        user_id=user.id,
        account_id=payload.to_account_id,
        source_type=SourceType.bank,
        source_id=f"transfer-in-{link_id}",
        amount=payload.amount,
        currency=payload.currency,
        booked_at=booked,
        merchant_clean=payload.description,
        description_raw=f"Transferencia desde {from_acc.name}",
        channel=TransactionChannel.transfer,
        status=TransactionStatus.booked,
    )
    db.add_all([tx_out, tx_in])
    db.flush()

    link = TransactionLink(
        user_id=user.id,
        left_transaction_id=tx_out.id,
        right_transaction_id=tx_in.id,
        link_type=LinkType.transfer_pair,
    )
    db.add(link)
    db.commit()
    db.refresh(tx_out)
    db.refresh(tx_in)
    return [
        TransactionResponse.model_validate(tx_payload(tx_out)),
        TransactionResponse.model_validate(tx_payload(tx_in)),
    ]


# ── Categories ───────────────────────────────────────────────

@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
):
    return (
        db.query(Category)
        .filter(Category.user_id == user.id)
        .order_by(Category.name.asc())
        .all()
    )


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(
    payload: CreateCategoryRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
):
    import re
    slug = re.sub(r"[^a-z0-9]+", "-", payload.name.lower()).strip("-")
    existing = (
        db.query(Category)
        .filter(Category.user_id == user.id, Category.slug == slug)
        .first()
    )
    if existing:
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"

    cat = Category(
        user_id=user.id,
        name=payload.name,
        slug=slug,
        color=payload.color,
        icon=payload.icon,
        parent_id=payload.parent_id,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: uuid.UUID,
    payload: UpdateCategoryRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
):
    cat = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user.id)
        .one_or_none()
    )
    if not cat:
        raise NotFoundError("category_not_found")
    if payload.name is not None:
        cat.name = payload.name
    if payload.color is not None:
        cat.color = payload.color
    if payload.icon is not None:
        cat.icon = payload.icon
    if payload.parent_id is not None:
        cat.parent_id = payload.parent_id
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/categories/{category_id}", status_code=204)
def delete_category(
    category_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
):
    cat = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user.id)
        .one_or_none()
    )
    if not cat:
        raise NotFoundError("category_not_found")
    db.query(Transaction).filter(
        Transaction.user_id == user.id,
        Transaction.category_id == category_id,
    ).update({"category_id": None})
    db.delete(cat)
    db.commit()


@router.get("/transactions/curve-duplicates", response_model=list[CurveDuplicateCandidateResponse])
def curve_duplicates(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[CurveDuplicateCandidateResponse]:
    return list_curve_duplicate_candidates(db, user.id)
