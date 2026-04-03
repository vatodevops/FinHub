from datetime import datetime, timezone
from decimal import Decimal

from app.models.entities import SourceType
from app.services.reconciliation import looks_like_curve_settlement, match_curve_to_bank


class DummyTx:
    def __init__(self, source_type, amount, currency, description_raw, booked_at):
        self.source_type = source_type
        self.amount = Decimal(amount)
        self.currency = currency
        self.description_raw = description_raw
        self.booked_at = booked_at


def test_looks_like_curve_settlement():
    assert looks_like_curve_settlement("CRV-1234 AMAZON")
    assert looks_like_curve_settlement("payment via curve*")
    assert not looks_like_curve_settlement("NETFLIX DIRECT")


def test_match_curve_to_bank():
    now = datetime.now(timezone.utc)
    curve_tx = DummyTx(SourceType.curve, "12.34", "EUR", "AMAZON", now)
    bank_tx = DummyTx(SourceType.bank, "12.34", "EUR", "CRV-9283 AMAZON", now)
    result = match_curve_to_bank(curve_tx, bank_tx)
    assert result.matched is True
    assert result.confidence > 0.9
