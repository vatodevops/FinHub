import uuid
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.asset import Asset, AssetType
from app.models.auth import User
from app.services import asset_service

router = APIRouter(dependencies=[Depends(require_auth)])


# ── Pydantic schemas ──────────────────────────────────────────────

class CreateAssetRequest(BaseModel):
    name: str
    type: AssetType
    currency: str = "EUR"
    units: Decimal | None = None
    valuation_method: str = "manual"
    purchase_date: date | None = None
    purchase_price: Decimal | None = None
    sell_date: date | None = None
    sell_price: Decimal | None = None
    growth_type: str | None = None
    growth_rate: Decimal | None = None
    growth_frequency: str | None = None
    growth_start_date: date | None = None
    ticker: str | None = None
    ticker_exchange: str | None = None
    last_price: Decimal | None = None
    logo_url: str | None = None
    external_id: str | None = None
    group_id: str | None = None


class UpdateAssetRequest(BaseModel):
    name: str | None = None
    type: AssetType | None = None
    currency: str | None = None
    units: Decimal | None = None
    valuation_method: str | None = None
    purchase_date: date | None = None
    purchase_price: Decimal | None = None
    sell_date: date | None = None
    sell_price: Decimal | None = None
    growth_type: str | None = None
    growth_rate: Decimal | None = None
    growth_frequency: str | None = None
    growth_start_date: date | None = None
    ticker: str | None = None
    ticker_exchange: str | None = None
    last_price: Decimal | None = None
    logo_url: str | None = None
    external_id: str | None = None
    group_id: str | None = None


class AssetValueRequest(BaseModel):
    amount: Decimal
    date: date
    source: str = "manual"


class AssetResponse(BaseModel):
    id: str
    name: str
    type: str
    currency: str
    units: Decimal | None
    valuation_method: str
    purchase_date: date | None
    purchase_price: Decimal | None
    sell_date: date | None
    sell_price: Decimal | None
    growth_type: str | None
    growth_rate: Decimal | None
    growth_frequency: str | None
    growth_start_date: date | None
    ticker: str | None
    ticker_exchange: str | None
    last_price: Decimal | None
    logo_url: str | None
    external_id: str | None
    source: str
    is_archived: bool
    current_value: Decimal
    group_id: str | None

    model_config = {"from_attributes": True}


class AssetValueResponse(BaseModel):
    id: str
    asset_id: str
    amount: Decimal
    date: date
    source: str
    created_at: date | None

    model_config = {"from_attributes": True}


class TotalValueResponse(BaseModel):
    total_value: Decimal
    currency: str


# ── Helpers ───────────────────────────────────────────────────────

def _asset_to_response(asset: Asset) -> dict:
    current_value = asset_service.calculate_current_value(asset)
    return {
        "id": str(asset.id),
        "name": asset.name,
        "type": asset.type.value if hasattr(asset.type, "value") else str(asset.type),
        "currency": asset.currency,
        "units": asset.units,
        "valuation_method": asset.valuation_method.value if hasattr(asset.valuation_method, "value") else str(asset.valuation_method),
        "purchase_date": asset.purchase_date,
        "purchase_price": asset.purchase_price,
        "sell_date": asset.sell_date,
        "sell_price": asset.sell_price,
        "growth_type": asset.growth_type.value if asset.growth_type and hasattr(asset.growth_type, "value") else asset.growth_type,
        "growth_rate": asset.growth_rate,
        "growth_frequency": asset.growth_frequency.value if asset.growth_frequency and hasattr(asset.growth_frequency, "value") else asset.growth_frequency,
        "growth_start_date": asset.growth_start_date,
        "ticker": asset.ticker,
        "ticker_exchange": asset.ticker_exchange,
        "last_price": asset.last_price,
        "logo_url": asset.logo_url,
        "external_id": asset.external_id,
        "source": asset.source.value if hasattr(asset.source, "value") else str(asset.source),
        "is_archived": asset.is_archived,
        "current_value": current_value,
        "group_id": str(asset.group.id) if asset.group else None,
    }


def _asset_value_to_response(value) -> dict:
    return {
        "id": str(value.id),
        "asset_id": str(value.asset_id),
        "amount": value.amount,
        "date": value.date,
        "source": value.source.value if hasattr(value.source, "value") else str(value.source),
        "created_at": value.created_at.date() if value.created_at else None,
    }


# ── Routes ────────────────────────────────────────────────────────

@router.get("", response_model=list[AssetResponse])
def list_assets(
    type: AssetType | None = None,
    is_archived: bool | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[AssetResponse]:
    assets = asset_service.get_assets(db, user.id, type=type, is_archived=is_archived)
    return [_asset_to_response(a) for a in assets]


@router.post("", response_model=AssetResponse, status_code=201)
def create_asset(
    payload: CreateAssetRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> AssetResponse:
    data = payload.model_dump(exclude_none=True)
    asset = asset_service.create_asset(db, user.id, **data)
    return _asset_to_response(asset)


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> AssetResponse:
    asset = asset_service.get_asset(db, str(asset_id), user.id)
    if asset is None:
        raise NotFoundError("asset_not_found")
    return _asset_to_response(asset)


@router.put("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: uuid.UUID,
    payload: UpdateAssetRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> AssetResponse:
    data = payload.model_dump(exclude_none=True)
    asset = asset_service.update_asset(db, str(asset_id), user.id, **data)
    return _asset_to_response(asset)


@router.delete("/{asset_id}", status_code=204)
def archive_asset(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
):
    asset_service.archive_asset(db, str(asset_id), user.id)


@router.get("/total-value", response_model=TotalValueResponse)
def get_total_value(
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> TotalValueResponse:
    total = asset_service.calculate_total_value(db, user.id)
    return TotalValueResponse(total_value=total, currency="EUR")


@router.get("/{asset_id}/values", response_model=list[AssetValueResponse])
def list_asset_values(
    asset_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[AssetValueResponse]:
    asset = asset_service.get_asset(db, str(asset_id), user.id)
    if asset is None:
        raise NotFoundError("asset_not_found")
    return [_asset_value_to_response(v) for v in asset.values]


@router.post("/{asset_id}/values", response_model=AssetValueResponse, status_code=201)
def add_asset_value(
    asset_id: uuid.UUID,
    payload: AssetValueRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> AssetValueResponse:
    asset = asset_service.get_asset(db, str(asset_id), user.id)
    if asset is None:
        raise NotFoundError("asset_not_found")

    from app.models.asset_value import AssetValue, AssetValueSource

    value = AssetValue(
        asset_id=str(asset_id),
        amount=payload.amount,
        date=payload.date,
        source=AssetValueSource(payload.source),
    )
    db.add(value)
    db.commit()
    db.refresh(value)
    return _asset_value_to_response(value)
