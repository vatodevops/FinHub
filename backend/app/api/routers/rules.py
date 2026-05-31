import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps.auth import require_auth
from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.models.auth import User
from app.models.rule import Rule
from app.services import rule_service

router = APIRouter()


# ── GET /rules ───────────────────────────────────────────────────────────

@router.get("/rules", response_model=list[dict])
def list_rules(
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> list[dict]:
    rules = rule_service.get_all_rules(db, user.id, active_only=active_only)
    return [rule_service._rule_to_dict(r) for r in rules]


# ── POST /rules ──────────────────────────────────────────────────────────

@router.post("/rules", response_model=dict, status_code=201)
def create_rule(
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> dict:
    if "name" not in payload:
        raise NotFoundError("name_required")
    rule = rule_service.create_rule(db, user.id, payload)
    return rule_service._rule_to_dict(rule)


# ── GET /rules/{id} ──────────────────────────────────────────────────────

@router.get("/rules/{rule_id}", response_model=dict)
def get_rule(
    rule_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> dict:
    rule = rule_service.get_rule(db, rule_id, user.id)
    if rule is None:
        raise NotFoundError("rule_not_found")
    return rule_service._rule_to_dict(rule)


# ── PUT /rules/{id} ──────────────────────────────────────────────────────

@router.put("/rules/{rule_id}", response_model=dict)
def update_rule(
    rule_id: uuid.UUID,
    payload: dict,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> dict:
    rule = rule_service.update_rule(db, rule_id, user.id, payload)
    return rule_service._rule_to_dict(rule)


# ── DELETE /rules/{id} ───────────────────────────────────────────────────

@router.delete("/rules/{rule_id}", status_code=204)
def delete_rule(
    rule_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> None:
    rule_service.delete_rule(db, rule_id, user.id)


# ── POST /rules/apply ────────────────────────────────────────────────────

@router.post("/rules/apply", response_model=dict)
def apply_rules(
    transaction_id: uuid.UUID = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_auth),
) -> dict:
    """Apply all active rules to a transaction identified by *transaction_id*."""
    from app.models.entities import Transaction

    txn = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == user.id)
        .first()
    )
    if txn is None:
        raise NotFoundError("transaction_not_found")

    # Build a plain dict from the transaction ORM object
    transaction = {
        "id": str(txn.id),
        "user_id": txn.user_id,
        "account_id": str(txn.account_id),
        "category_id": str(txn.category_id) if txn.category_id else None,
        "source_type": txn.source_type.value if hasattr(txn.source_type, "value") else str(txn.source_type),
        "source_id": txn.source_id,
        "amount": float(txn.amount) if txn.amount else None,
        "currency": txn.currency,
        "booked_at": txn.booked_at.isoformat() if txn.booked_at else None,
        "value_date": txn.value_date.isoformat() if txn.value_date else None,
        "merchant_raw": txn.merchant_raw,
        "merchant_clean": txn.merchant_clean,
        "description_raw": txn.description_raw,
        "channel": txn.channel.value if hasattr(txn.channel, "value") else str(txn.channel),
        "status": txn.status.value if hasattr(txn.status, "value") else str(txn.status),
        "fingerprint": txn.fingerprint,
    }

    result = rule_service.apply_rules_to_transaction(db, user.id, transaction)
    return result
