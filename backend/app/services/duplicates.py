from sqlalchemy.orm import Session

from app.models.entities import SourceType, Transaction
from app.schemas.duplicates import CurveDuplicateCandidateResponse
from app.schemas.transactions import TransactionResponse
from app.services.reconciliation import match_curve_to_bank


def list_curve_duplicate_candidates(db: Session) -> list[CurveDuplicateCandidateResponse]:
    curve_txs = db.query(Transaction).filter(Transaction.source_type == SourceType.curve).all()
    bank_txs = db.query(Transaction).filter(Transaction.source_type == SourceType.bank).all()
    out: list[CurveDuplicateCandidateResponse] = []

    for curve_tx in curve_txs:
        for bank_tx in bank_txs:
            result = match_curve_to_bank(curve_tx, bank_tx)
            if result.matched:
                out.append(
                    CurveDuplicateCandidateResponse(
                        confidence=result.confidence,
                        reason=result.reason,
                        curve_transaction=TransactionResponse.model_validate(_tx_payload(curve_tx)),
                        bank_transaction=TransactionResponse.model_validate(_tx_payload(bank_tx)),
                    )
                )
    return out


def _tx_payload(tx: Transaction) -> dict:
    return {
        "id": tx.id,
        "account_id": tx.account_id,
        "category_id": tx.category_id,
        "category_name": tx.category.name if getattr(tx, 'category', None) else None,
        "source_type": tx.source_type.value if hasattr(tx.source_type, 'value') else tx.source_type,
        "source_id": tx.source_id,
        "amount": tx.amount,
        "currency": tx.currency,
        "booked_at": tx.booked_at,
        "value_date": tx.value_date,
        "merchant_raw": tx.merchant_raw,
        "merchant_clean": tx.merchant_clean,
        "description_raw": tx.description_raw,
        "channel": tx.channel.value if hasattr(tx.channel, 'value') else tx.channel,
        "status": tx.status.value if hasattr(tx.status, 'value') else tx.status,
    }
