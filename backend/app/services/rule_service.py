"""Rule CRUD service and transaction-rule application."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import NotFoundError
from app.models.rule import Rule
from app.services.rule_engine import apply_actions, evaluate_conditions


# ── Universal default rules ──────────────────────────────────────────────

UNIVERSAL_RULES: list[dict[str, Any]] = [
    # Netflix
    {
        "name": "Netflix subscription",
        "conditions_op": "or",
        "conditions": [
            {"field": "merchant_clean", "op": "equals", "value": "netflix"},
            {"field": "merchant_raw", "op": "contains", "value": "netflix"},
        ],
        "actions": [{"action": "set_category", "value": "subscriptions"}],
        "priority": 10,
    },
    # Spotify
    {
        "name": "Spotify subscription",
        "conditions_op": "or",
        "conditions": [
            {"field": "merchant_clean", "op": "equals", "value": "spotify"},
            {"field": "merchant_raw", "op": "contains", "value": "spotify"},
        ],
        "actions": [{"action": "set_category", "value": "subscriptions"}],
        "priority": 10,
    },
    # Uber
    {
        "name": "Uber ride",
        "conditions_op": "or",
        "conditions": [
            {"field": "merchant_clean", "op": "equals", "value": "uber"},
            {"field": "merchant_raw", "op": "contains", "value": "uber"},
        ],
        "actions": [{"action": "set_category", "value": "transport"}],
        "priority": 10,
    },
    # Amazon
    {
        "name": "Amazon purchase",
        "conditions_op": "or",
        "conditions": [
            {"field": "merchant_clean", "op": "equals", "value": "amazon"},
            {"field": "merchant_raw", "op": "contains", "value": "amazon"},
        ],
        "actions": [{"action": "set_category", "value": "shopping"}],
        "priority": 10,
    },
    # Apple subscriptions
    {
        "name": "Apple subscription",
        "conditions_op": "or",
        "conditions": [
            {"field": "merchant_raw", "op": "contains", "value": "apple.com"},
            {"field": "merchant_raw", "op": "contains", "value": "apple.com/bill"},
            {"field": "merchant_clean", "op": "contains", "value": "apple"},
        ],
        "actions": [{"action": "set_category", "value": "subscriptions"}],
        "priority": 10,
    },
    # Google Play / Google subscriptions
    {
        "name": "Google subscription",
        "conditions_op": "or",
        "conditions": [
            {"field": "merchant_raw", "op": "contains", "value": "google.com"},
            {"field": "merchant_raw", "op": "contains", "value": "google play"},
            {"field": "merchant_clean", "op": "contains", "value": "google"},
        ],
        "actions": [{"action": "set_category", "value": "subscriptions"}],
        "priority": 10,
    },
    # Apple App Store
    {
        "name": "Apple App Store",
        "conditions_op": "or",
        "conditions": [
            {"field": "merchant_raw", "op": "contains", "value": "app store"},
            {"field": "merchant_raw", "op": "contains", "value": "apple.com/pay"},
        ],
        "actions": [{"action": "set_category", "value": "shopping"}],
        "priority": 10,
    },
    # Google Play Store
    {
        "name": "Google Play Store",
        "conditions_op": "or",
        "conditions": [
            {"field": "merchant_raw", "op": "contains", "value": "google play store"},
        ],
        "actions": [{"action": "set_category", "value": "shopping"}],
        "priority": 10,
    },
    # Salary / payroll
    {
        "name": "Salary / payroll",
        "conditions_op": "or",
        "conditions": [
            {"field": "merchant_raw", "op": "contains", "value": "salary"},
            {"field": "merchant_raw", "op": "contains", "value": "payroll"},
            {"field": "merchant_raw", "op": "contains", "value": "nominativo"},
            {"field": "merchant_raw", "op": "contains", "value": "nomina"},
            {"field": "merchant_raw", "op": "contains", "value": "wage"},
        ],
        "actions": [{"action": "set_category", "value": "income"}],
        "priority": 10,
    },
]


# ── CRUD helpers ─────────────────────────────────────────────────────────

def _rule_to_dict(rule: Rule) -> dict[str, Any]:
    """Serialize a Rule ORM object to a plain dict."""
    return {
        "id": str(rule.id),
        "user_id": rule.user_id,
        "name": rule.name,
        "conditions_op": rule.conditions_op,
        "conditions": rule.conditions,
        "actions": rule.actions,
        "priority": rule.priority,
        "is_active": rule.is_active,
        "created_at": rule.created_at.isoformat() if rule.created_at else None,
        "updated_at": rule.updated_at.isoformat() if rule.updated_at else None,
    }


def create_rule(db: Session, user_id: str, data: dict[str, Any]) -> Rule:
    """Create a new rule for the given user."""
    rule = Rule(
        user_id=user_id,
        name=data["name"],
        conditions_op=data.get("conditions_op", "and"),
        conditions=data.get("conditions", []),
        actions=data.get("actions", []),
        priority=data.get("priority", 0),
        is_active=data.get("is_active", True),
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def update_rule(
    db: Session,
    rule_id: uuid.UUID,
    user_id: str,
    data: dict[str, Any],
) -> Rule:
    """Update an existing rule (must belong to user)."""
    rule = (
        db.query(Rule)
        .filter(Rule.id == rule_id, Rule.user_id == user_id)
        .first()
    )
    if rule is None:
        raise NotFoundError("rule_not_found")

    if "name" in data:
        rule.name = data["name"]
    if "conditions_op" in data:
        rule.conditions_op = data["conditions_op"]
    if "conditions" in data:
        rule.conditions = data["conditions"]
    if "actions" in data:
        rule.actions = data["actions"]
    if "priority" in data:
        rule.priority = data["priority"]
    if "is_active" in data:
        rule.is_active = data["is_active"]

    db.commit()
    db.refresh(rule)
    return rule


def get_rule(db: Session, rule_id: uuid.UUID, user_id: str) -> Rule | None:
    """Get a single rule by id, scoped to user."""
    return (
        db.query(Rule)
        .filter(Rule.id == rule_id, Rule.user_id == user_id)
        .first()
    )


def get_all_rules(db: Session, user_id: str, active_only: bool = False) -> list[Rule]:
    """List all rules for a user, ordered by priority desc then created_at desc."""
    q = db.query(Rule).filter(Rule.user_id == user_id)
    if active_only:
        q = q.filter(Rule.is_active == True)  # noqa: E712
    return q.order_by(Rule.priority.desc(), Rule.created_at.desc()).all()


def delete_rule(db: Session, rule_id: uuid.UUID, user_id: str) -> None:
    """Delete a rule (must belong to user)."""
    rule = (
        db.query(Rule)
        .filter(Rule.id == rule_id, Rule.user_id == user_id)
        .first()
    )
    if rule is None:
        raise NotFoundError("rule_not_found")
    db.delete(rule)
    db.commit()


# ── Apply rules to a transaction ─────────────────────────────────────────

def apply_rules_to_transaction(
    db: Session,
    user_id: str,
    transaction: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate all active rules for *user_id* against *transaction*.

    Rules are ordered by priority descending. The first matching rule's
    actions are applied and the enriched transaction is returned.
    """
    rules = (
        db.query(Rule)
        .filter(Rule.user_id == user_id, Rule.is_active == True)  # noqa: E712
        .order_by(Rule.priority.desc(), Rule.created_at.desc())
        .all()
    )

    category_id = transaction.get("category_id")
    category_already_set = category_id is not None

    for rule in rules:
        if evaluate_conditions(rule.conditions_op, rule.conditions, transaction):
            if rule.actions:
                transaction = apply_actions(rule.actions, transaction, category_already_set)
            break

    return transaction
