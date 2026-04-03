from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from app.models.entities import SourceType, Transaction


@dataclass
class MatchResult:
    matched: bool
    reason: str
    confidence: float


CURVE_HINTS = ("CRV-", "CURVE")


def looks_like_curve_settlement(description: str | None) -> bool:
    if not description:
        return False
    upper = description.upper()
    return any(hint in upper for hint in CURVE_HINTS)


def match_curve_to_bank(curve_tx: Transaction, bank_tx: Transaction) -> MatchResult:
    if curve_tx.source_type != SourceType.curve or bank_tx.source_type != SourceType.bank:
        return MatchResult(False, "wrong source types", 0.0)

    if Decimal(curve_tx.amount) != Decimal(bank_tx.amount):
        return MatchResult(False, "different amount", 0.0)

    if curve_tx.currency != bank_tx.currency:
        return MatchResult(False, "different currency", 0.0)

    if not looks_like_curve_settlement(bank_tx.description_raw):
        return MatchResult(False, "bank transaction does not look like curve settlement", 0.15)

    if curve_tx.booked_at and bank_tx.booked_at:
        if abs(curve_tx.booked_at - bank_tx.booked_at) > timedelta(days=3):
            return MatchResult(False, "outside matching window", 0.2)

    return MatchResult(True, "curve settlement match", 0.95)
