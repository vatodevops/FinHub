import logging
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.core.exceptions import ExternalServiceError, NotFoundError
from app.db.session import get_db
from app.models.auth import User
from app.models.bank_connection import BankConnection, BankConnectionStatus
from app.schemas.bank_connection import BankConnectionResponse
from app.services.connectors.banks.gocardless import GoCardlessBankConnector
from app.services.connectors.banks.gocardless_client import GoCardlessClient, GoCardlessConfigError
from app.services.sync.bank_sync import sync_bank_connection

logger = logging.getLogger("finhub")

router = APIRouter()


@router.get("/connectors/gocardless/institutions")
async def gocardless_institutions(
    country: str = Query(default="ES"),
    user: User = Depends(require_auth),
):
    try:
        client = GoCardlessClient()
        return await client.list_institutions(country=country)
    except GoCardlessConfigError as exc:
        raise ExternalServiceError(str(exc))


@router.get("/bank-connections", response_model=list[BankConnectionResponse])
def list_bank_connections(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[BankConnectionResponse]:
    return (
        db.query(BankConnection)
        .filter(BankConnection.user_id == user.id)
        .order_by(BankConnection.created_at.desc())
        .all()
    )


@router.post("/connectors/gocardless/requisition", response_model=BankConnectionResponse)
async def gocardless_requisition(
    institution_id: str = Query(...),
    reference: str = Query(...),
    institution_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
):
    connector = GoCardlessBankConnector()
    requisition = await connector.client.create_requisition(institution_id=institution_id, reference=reference)
    connection = BankConnection(
        user_id=user.id,
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
async def refresh_bank_connection(
    connection_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> BankConnectionResponse:
    connection = (
        db.query(BankConnection)
        .filter(BankConnection.id == connection_id, BankConnection.user_id == user.id)
        .one_or_none()
    )
    if connection is None:
        raise NotFoundError("connection_not_found")
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
        logger.error("Failed to refresh connection %s: %s", connection_id, exc)
        connection.status = BankConnectionStatus.failed
        connection.error_message = str(exc)
        db.commit()
        db.refresh(connection)
        return connection


@router.post("/bank-connections/{connection_id}/sync")
async def run_bank_connection_sync(
    connection_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
):
    connection = (
        db.query(BankConnection)
        .filter(BankConnection.id == connection_id, BankConnection.user_id == user.id)
        .one_or_none()
    )
    if connection is None:
        raise NotFoundError("connection_not_found")
    try:
        return await sync_bank_connection(db, connection)
    except Exception as exc:
        logger.error("Failed to sync connection %s: %s", connection_id, exc)
        connection.status = BankConnectionStatus.failed
        connection.error_message = str(exc)
        db.commit()
        return {"error": str(exc), "connection_id": str(connection.id)}
