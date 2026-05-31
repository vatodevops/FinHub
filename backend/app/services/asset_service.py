"""Asset CRUD and calculation service."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import NotFoundError
from app.models.asset import Asset, AssetSource, AssetType, GrowthFrequency, GrowthType, ValuationMethod
from app.models.asset_value import AssetValue

if TYPE_CHECKING:
    from app.models.asset_group import AssetGroup


def create_asset(session: Session, user_id: str, **data) -> Asset:
    """Create a new asset for the given user."""
    # Validate valuation_method defaults
    if "valuation_method" not in data or data["valuation_method"] is None:
        data["valuation_method"] = ValuationMethod.manual

    # Validate source defaults
    if "source" not in data or data["source"] is None:
        data["source"] = AssetSource.manual

    # Validate currency defaults
    if "currency" not in data or data["currency"] is None:
        data["currency"] = "EUR"

    # Validate is_archived defaults
    if "is_archived" not in data:
        data["is_archived"] = False

    asset = Asset(user_id=user_id, **data)
    session.add(asset)
    session.commit()
    session.refresh(asset)
    return asset


def get_asset(session: Session, asset_id: str, user_id: str) -> Asset | None:
    """Get a single asset by id, scoped to user."""
    stmt = (
        select(Asset)
        .where(Asset.id == asset_id, Asset.user_id == user_id)
        .options(selectinload(Asset.values), selectinload(Asset.group))
    )
    return session.execute(stmt).scalar_one_or_none()


def get_assets(
    session: Session,
    user_id: str,
    type: AssetType | None = None,
    is_archived: bool | None = None,
) -> list[Asset]:
    """List assets for a user with optional filters."""
    stmt = select(Asset).where(Asset.user_id == user_id)

    if type is not None:
        stmt = stmt.where(Asset.type == type)

    if is_archived is not None:
        stmt = stmt.where(Asset.is_archived == is_archived)
    else:
        # Default: show only non-archived
        stmt = stmt.where(Asset.is_archived == False)  # noqa: E712

    stmt = stmt.order_by(Asset.created_at.desc())
    return list(session.execute(stmt).scalars().all())


def update_asset(session: Session, asset_id: str, user_id: str, **data) -> Asset:
    """Update an existing asset (must belong to user)."""
    stmt = (
        select(Asset)
        .where(Asset.id == asset_id, Asset.user_id == user_id)
        .options(selectinload(Asset.values), selectinload(Asset.group))
    )
    asset = session.execute(stmt).scalar_one_or_none()

    if asset is None:
        raise NotFoundError("asset_not_found")

    # Fields that can be updated
    updatable = {
        "name", "type", "currency", "units", "valuation_method",
        "purchase_date", "purchase_price", "sell_date", "sell_price",
        "growth_type", "growth_rate", "growth_frequency", "growth_start_date",
        "ticker", "ticker_exchange", "last_price", "last_price_at",
        "logo_url", "external_id", "external_metadata", "group_id",
    }

    for key, value in data.items():
        if key in updatable:
            setattr(asset, key, value)

    session.commit()
    session.refresh(asset)
    return asset


def archive_asset(session: Session, asset_id: str, user_id: str) -> Asset:
    """Archive an asset (soft delete)."""
    stmt = (
        select(Asset)
        .where(Asset.id == asset_id, Asset.user_id == user_id)
        .options(selectinload(Asset.values), selectinload(Asset.group))
    )
    asset = session.execute(stmt).scalar_one_or_none()

    if asset is None:
        raise NotFoundError("asset_not_found")

    asset.is_archived = True
    session.commit()
    session.refresh(asset)
    return asset


def calculate_current_value(asset: Asset) -> Decimal:
    """Calculate the current value of an asset.

    Priority:
    1. If valuation_method is market_price and last_price is set, use it * units.
    2. If valuation_method is growth_rule and growth_rate is set, compound from purchase_price.
    3. If there are AssetValue records, use the latest one.
    4. Fall back to purchase_price if available.
    """
    # Market price method
    if asset.valuation_method == ValuationMethod.market_price and asset.last_price is not None:
        units = asset.units or Decimal("1")
        return asset.last_price * units

    # Growth rule method
    if (
        asset.valuation_method == ValuationMethod.growth_rule
        and asset.growth_rate is not None
        and asset.growth_start_date is not None
        and asset.purchase_price is not None
    ):
        return _compound_growth(
            principal=asset.purchase_price,
            growth_rate=asset.growth_rate,
            growth_type=asset.growth_type,
            frequency=asset.growth_frequency,
            start_date=asset.growth_start_date,
        )

    # Latest AssetValue
    if asset.values:
        latest = max(asset.values, key=lambda v: v.date)
        return latest.amount

    # Fallback to purchase_price
    if asset.purchase_price is not None:
        return asset.purchase_price

    return Decimal("0")


def _compound_growth(
    principal: Decimal,
    growth_rate: Decimal,
    growth_type: GrowthType | None,
    frequency: GrowthFrequency | None,
    start_date: date,
) -> Decimal:
    """Compound a growth rate from start_date to today."""
    days = (date.today() - start_date).days
    if days <= 0:
        return principal

    # Map frequency to periods per year
    freq_map = {
        "daily": 365,
        "weekly": 52,
        "monthly": 12,
        "yearly": 1,
    }

    periods_per_year = freq_map.get(str(frequency), 12) if frequency else 12
    periods = Decimal(str(days)) * Decimal(str(periods_per_year)) / Decimal("365")

    if growth_type == GrowthType.percentage:
        rate = growth_rate / Decimal("100")
    else:
        # absolute: growth_rate is added per period
        rate = growth_rate

    if growth_type == GrowthType.absolute:
        return principal + (principal * rate * periods)

    # Compound: principal * (1 + rate)^periods
    if rate >= 0:
        return principal * (Decimal("1") + rate) ** int(periods)
    else:
        return principal * (Decimal("1") - (-rate)) ** int(periods)


def calculate_total_value(session: Session, user_id: str) -> Decimal:
    """Sum the current values of all non-archived assets for a user."""
    stmt = (
        select(Asset)
        .where(Asset.user_id == user_id, Asset.is_archived == False)  # noqa: E712
        .options(selectinload(Asset.values))
    )
    assets = list(session.execute(stmt).scalars().all())
    total = Decimal("0")
    for asset in assets:
        total += calculate_current_value(asset)
    return total


def calculate_growth_rate(asset: Asset) -> Decimal:
    """Calculate the growth rate of an asset.

    Priority:
    1. Use stored growth_rate from growth_rule config.
    2. If AssetValue history exists, compute from first to latest value.
    3. Fall back to 0.
    """
    # Use configured growth rate
    if asset.growth_rate is not None:
        return asset.growth_rate

    # Compute from price history
    if asset.values and len(asset.values) >= 2:
        sorted_values = sorted(asset.values, key=lambda v: v.date)
        first_value = sorted_values[0].amount
        last_value = sorted_values[-1].amount
        if first_value > 0:
            return ((last_value - first_value) / first_value) * Decimal("100")

    # Compute from purchase/sell prices
    if asset.purchase_price is not None and asset.purchase_price > 0:
        current = calculate_current_value(asset)
        if current > 0:
            return ((current - asset.purchase_price) / asset.purchase_price) * Decimal("100")

    return Decimal("0")
