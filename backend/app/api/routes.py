import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.bank_connection import BankConnection, BankConnectionStatus
from app.models.categories import Category
from app.models.entities import Account, Institution, Transaction
from app.models.manual import ManualItemKind, ManualItemStatus, ManualPlannedItem
from app.models.recurring import RecurringOccurrence, RecurringSeries
from app.schemas.accounts import AccountResponse
from app.schemas.bank_connection import BankConnectionResponse
from app.schemas.categories import CategoryResponse, TransactionCategoryUpdate
from app.schemas.duplicates import CurveDuplicateCandidateResponse
from app.schemas.health import HealthResponse
from app.schemas.institutions import InstitutionResponse
from app.schemas.manual import ManualPlannedItemCreate, ManualPlannedItemResponse
from app.schemas.overview import OverviewResponse
from app.schemas.recurring import RecurringOccurrenceResponse, RecurringSeriesResponse
from app.schemas.transactions import TransactionResponse
from app.services.connectors.banks.gocardless import GoCardlessBankConnector
from app.services.connectors.banks.gocardless_client import GoCardlessClient, GoCardlessConfigError
from app.services.duplicates import list_curve_duplicate_candidates
from app.services.overview import build_overview
from app.services.recurring_detection import detect_monthly_candidates
from app.services.sync.bank_sync import sync_bank_connection

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name)


@router.get("/overview", response_model=OverviewResponse)
def overview(db: Session = Depends(get_db)) -> OverviewResponse:
    return build_overview(db)


@router.get("/institutions", response_model=list[InstitutionResponse])
def list_institutions(db: Session = Depends(get_db)) -> list[InstitutionResponse]:
    return db.query(Institution).order_by(Institution.name.asc()).all()


@router.get("/accounts", response_model=list[AccountResponse])
def list_accounts(db: Session = Depends(get_db)) -> list[AccountResponse]:
    return db.query(Account).order_by(Account.name.asc()).all()


@router.get("/transactions", response_model=list[TransactionResponse])
def list_transactions(
    account_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[TransactionResponse]:
    query = db.query(Transaction)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    rows = query.order_by(Transaction.booked_at.desc().nullslast(), Transaction.created_at.desc()).limit(limit).all()
    return [TransactionResponse.model_validate(_tx_payload(tx)) for tx in rows]


@router.get("/categories", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)) -> list[CategoryResponse]:
    return db.query(Category).order_by(Category.name.asc()).all()


@router.patch("/transactions/{transaction_id}/category", response_model=TransactionResponse)
def update_transaction_category(
    transaction_id: uuid.UUID,
    payload: TransactionCategoryUpdate,
    db: Session = Depends(get_db),
) -> TransactionResponse:
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).one_or_none()
    if tx is None:
        raise HTTPException(status_code=404, detail="transaction_not_found")
    tx.category_id = payload.category_id
    db.commit()
    db.refresh(tx)
    return TransactionResponse.model_validate(_tx_payload(tx))


@router.get("/transactions/curve-duplicates", response_model=list[CurveDuplicateCandidateResponse])
def curve_duplicates(db: Session = Depends(get_db)) -> list[CurveDuplicateCandidateResponse]:
    return list_curve_duplicate_candidates(db)


@router.get("/recurring/series", response_model=list[RecurringSeriesResponse])
def list_recurring_series(db: Session = Depends(get_db)) -> list[RecurringSeriesResponse]:
    return db.query(RecurringSeries).order_by(RecurringSeries.next_expected_date.asc().nullslast()).all()


@router.get("/recurring/calendar", response_model=list[RecurringOccurrenceResponse])
def recurring_calendar(
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[RecurringOccurrenceResponse]:
    return (
        db.query(RecurringOccurrence)
        .order_by(RecurringOccurrence.expected_date.asc(), RecurringOccurrence.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/recurring/suggestions")
def recurring_suggestions(
    account_id: uuid.UUID | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    txs = query.all()
    return detect_monthly_candidates(txs)


@router.get("/manual/planned-items", response_model=list[ManualPlannedItemResponse])
def list_manual_planned_items(db: Session = Depends(get_db)) -> list[ManualPlannedItemResponse]:
    return db.query(ManualPlannedItem).order_by(ManualPlannedItem.expected_date.asc().nullslast()).all()


@router.post("/manual/planned-items", response_model=ManualPlannedItemResponse)
def create_manual_planned_item(payload: ManualPlannedItemCreate, db: Session = Depends(get_db)) -> ManualPlannedItemResponse:
    item = ManualPlannedItem(
        account_id=payload.account_id,
        name=payload.name,
        merchant_hint=payload.merchant_hint,
        kind=ManualItemKind(payload.kind),
        amount=payload.amount,
        currency=payload.currency,
        expected_date=payload.expected_date,
        recurrence_rule=payload.recurrence_rule,
        status=ManualItemStatus(payload.status),
        notes=payload.notes,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/connectors/gocardless/institutions")
async def gocardless_institutions(country: str = Query(default="ES")):
    try:
        client = GoCardlessClient()
        return await client.list_institutions(country=country)
    except GoCardlessConfigError as exc:
        return {"error": str(exc), "configured": False}


@router.get("/bank-connections", response_model=list[BankConnectionResponse])
def list_bank_connections(db: Session = Depends(get_db)) -> list[BankConnectionResponse]:
    return db.query(BankConnection).order_by(BankConnection.created_at.desc()).all()


@router.post("/connectors/gocardless/requisition", response_model=BankConnectionResponse)
async def gocardless_requisition(
    institution_id: str = Query(...),
    reference: str = Query(...),
    institution_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    connector = GoCardlessBankConnector()
    requisition = await connector.client.create_requisition(institution_id=institution_id, reference=reference)
    connection = BankConnection(
        provider="gocardless_bad",
        requisition_id=requisition["id"],
        reference=reference,
        institution_external_id=institution_id,
        institution_name=institution_name,
        link=requisition.get("link"),
        status=BankConnectionStatus.pending,
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


@router.post("/bank-connections/{connection_id}/refresh", response_model=BankConnectionResponse)
async def refresh_bank_connection(connection_id: uuid.UUID, db: Session = Depends(get_db)) -> BankConnectionResponse:
    connection = db.query(BankConnection).filter(BankConnection.id == connection_id).one_or_none()
    if connection is None:
        raise HTTPException(status_code=404, detail="connection_not_found")
    try:
        client = GoCardlessClient()
        req = await client.get_requisition(connection.requisition_id)
        connection.link = req.get("link")
        accounts = req.get("accounts", [])
        connection.status = BankConnectionStatus.linked if accounts else BankConnectionStatus.pending
        connection.error_message = None
        db.commit()
        db.refresh(connection)
        return connection
    except Exception as exc:
        connection.status = BankConnectionStatus.failed
        connection.error_message = str(exc)
        db.commit()
        db.refresh(connection)
        return connection


@router.post("/bank-connections/{connection_id}/sync")
async def run_bank_connection_sync(connection_id: uuid.UUID, db: Session = Depends(get_db)):
    connection = db.query(BankConnection).filter(BankConnection.id == connection_id).one_or_none()
    if connection is None:
        return {"error": "connection_not_found"}
    try:
        return await sync_bank_connection(db, connection)
    except Exception as exc:
        connection.status = BankConnectionStatus.failed
        connection.error_message = str(exc)
        db.commit()
        return {"error": str(exc), "connection_id": str(connection.id)}


def _tx_payload(tx: Transaction) -> dict:
    return {
        "id": tx.id,
        "account_id": tx.account_id,
        "category_id": tx.category_id,
        "category_name": tx.category.name if getattr(tx, "category", None) else None,
        "source_type": tx.source_type.value if hasattr(tx.source_type, "value") else tx.source_type,
        "source_id": tx.source_id,
        "amount": tx.amount,
        "currency": tx.currency,
        "booked_at": tx.booked_at,
        "value_date": tx.value_date,
        "merchant_raw": tx.merchant_raw,
        "merchant_clean": tx.merchant_clean,
        "description_raw": tx.description_raw,
        "channel": tx.channel.value if hasattr(tx.channel, "value") else tx.channel,
        "status": tx.status.value if hasattr(tx.status, "value") else tx.status,
    }
