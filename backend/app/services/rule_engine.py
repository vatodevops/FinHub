"""Pure rule-evaluation engine. No database access."""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any

# Fields that can be referenced in conditions
SUPPORTED_FIELDS = frozenset({
    "description_raw",
    "merchant_raw",
    "merchant_clean",
    "amount",
    "currency",
    "channel",
    "source_type",
})

# Supported operators
SUPPORTED_OPS = frozenset({
    "contains",
    "not_contains",
    "starts_with",
    "ends_with",
    "equals",
    "not_equals",
    "regex",
    "gt",
    "gte",
    "lt",
    "lte",
})


def _normalize(text: str | None) -> str:
    """Accent-insensitive, lowercased normalisation for string comparisons."""
    if text is None:
        return ""
    return text.casefold().strip()


def _field_value(condition: dict[str, Any]) -> Any:
    """Return the field name and the value to compare against from a condition dict."""
    return condition.get("field"), condition.get("value")


def _match_condition(condition: dict[str, Any], transaction: dict[str, Any]) -> bool:
    """Evaluate a single condition against a transaction dict."""
    field = condition.get("field")
    op = condition.get("op")
    value = condition.get("value")

    if field not in SUPPORTED_FIELDS:
        return False
    if op not in SUPPORTED_OPS:
        return False

    raw = transaction.get(field)

    # ── String ops (operate on normalised text) ──
    if op in ("contains", "not_contains", "starts_with", "ends_with", "equals", "not_equals"):
        norm_raw = _normalize(raw)
        norm_val = _normalize(value) if value is not None else ""
        if op == "contains":
            return norm_val in norm_raw
        if op == "not_contains":
            return norm_val not in norm_raw
        if op == "starts_with":
            return norm_raw.startswith(norm_val)
        if op == "ends_with":
            return norm_raw.endswith(norm_val)
        if op == "equals":
            return norm_raw == norm_val
        if op == "not_equals":
            return norm_raw != norm_val

    # ── Regex ──
    if op == "regex":
        norm_raw = _normalize(raw)
        norm_val = _normalize(value) if value is not None else ""
        try:
            return bool(re.search(norm_val, norm_raw))
        except re.error:
            return False

    # ── Numeric ops (amount) ──
    if op in ("gt", "gte", "lt", "lte"):
        if field != "amount":
            return False
        try:
            t_val = Decimal(str(raw)) if raw is not None else None
        except (TypeError, ValueError):
            return False
        try:
            cmp_val = Decimal(str(value))
        except (TypeError, ValueError):
            return False
        if t_val is None:
            return False
        if op == "gt":
            return t_val > cmp_val
        if op == "gte":
            return t_val >= cmp_val
        if op == "lt":
            return t_val < cmp_val
        if op == "lte":
            return t_val <= cmp_val

    return False


def evaluate_conditions(
    conditions_op: str,
    conditions: list[dict[str, Any]],
    transaction: dict[str, Any],
) -> bool:
    """Evaluate a list of conditions against a transaction dict.

    * ``conditions_op`` is ``"and"`` or ``"or"``.
    * ``conditions`` is a list of dicts with keys ``field``, ``op``, ``value``.

    Returns ``True`` when the condition set matches.
    """
    if not conditions:
        return True

    if conditions_op == "or":
        return any(_match_condition(c, transaction) for c in conditions)
    # default: "and"
    return all(_match_condition(c, transaction) for c in conditions)


def apply_actions(
    actions: list[dict[str, Any]],
    transaction: dict[str, Any],
    category_already_set: bool = False,
) -> dict[str, Any]:
    """Apply a list of actions to a transaction dict and return the updated dict.

    Supported actions:
    - ``{"action": "set_category", "value": "<category_id_or_name>"}``
    - ``{"action": "set_payee", "value": "<payee name>"}``
    - ``{"action": "set_description", "value": "<description>"}``
    - ``{"action": "set_notes", "value": "<notes>"}``

    ``set_category`` is skipped when ``category_already_set`` is ``True``.
    """
    result = dict(transaction)

    for action in actions:
        act = action.get("action")
        val = action.get("value")
        if act is None:
            continue

        if act == "set_category" and not category_already_set:
            result["category_id"] = val
        elif act == "set_payee":
            result["merchant_clean"] = val
        elif act == "set_description":
            result["description_raw"] = val
        elif act == "set_notes":
            result.setdefault("notes", "")
            result["notes"] = val

    return result
