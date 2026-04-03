from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from app.models.entities import Transaction, TransactionChannel
from app.models.recurring import RecurrenceState, RecurrenceType


@dataclass
class RecurringCandidate:
    account_id: str | None
    name: str
    merchant_clean: str | None
    recurrence_type: RecurrenceType
    interval_days: int
    typical_day_of_month: int | None
    amount_mean: Decimal
    amount_deviation: Decimal
    next_expected_date: date | None
    confidence: Decimal
    state: RecurrenceState = RecurrenceState.auto_detected


def _merchant_key(tx: Transaction) -> str | None:
    base = (tx.merchant_clean or tx.merchant_raw or tx.description_raw or "").strip().upper()
    return base or None


def detect_monthly_candidates(transactions: list[Transaction]) -> list[RecurringCandidate]:
    groups: dict[tuple[str | None, str], list[Transaction]] = defaultdict(list)
    for tx in transactions:
        if tx.channel not in {TransactionChannel.card, TransactionChannel.direct_debit}:
            continue
        if tx.booked_at is None:
            continue
        key = _merchant_key(tx)
        if not key:
            continue
        groups[(str(tx.account_id), key)].append(tx)

    candidates: list[RecurringCandidate] = []
    for (account_id, merchant_key), items in groups.items():
        items = sorted(items, key=lambda t: t.booked_at)
        if len(items) < 3:
            continue

        dates = [t.booked_at.date() for t in items]
        gaps = [(dates[i] - dates[i - 1]).days for i in range(1, len(dates))]
        monthly_like = [g for g in gaps if 26 <= g <= 33]
        if len(monthly_like) < 2:
            continue

        amounts = [Decimal(t.amount) for t in items]
        mean = sum(amounts) / len(amounts)
        deviation = max(abs(a - mean) for a in amounts)
        typical_day = round(sum(d.day for d in dates) / len(dates))
        next_expected = dates[-1] + timedelta(days=30)
        confidence = Decimal("0.75") if deviation <= Decimal("5.00") else Decimal("0.60")

        candidates.append(
            RecurringCandidate(
                account_id=account_id,
                name=items[-1].merchant_clean or items[-1].merchant_raw or merchant_key.title(),
                merchant_clean=items[-1].merchant_clean or merchant_key.title(),
                recurrence_type=RecurrenceType.monthly,
                interval_days=30,
                typical_day_of_month=typical_day,
                amount_mean=mean.quantize(Decimal("0.01")),
                amount_deviation=deviation.quantize(Decimal("0.01")),
                next_expected_date=next_expected,
                confidence=confidence,
            )
        )

    return candidates
