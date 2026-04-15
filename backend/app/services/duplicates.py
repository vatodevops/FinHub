from sqlalchemy.orm import Session

from app.models.entities import SourceType, Transaction
from app.schemas.duplicates import CurveDuplicateCandidateResponse
from app.schemas.transactions import TransactionResponse, tx_payload
from app.services.reconciliation import match_curve_to_bank


def list_curve_duplicate_candidates(db: Session, user_id) -> list[CurveDuplicateCandidateResponse]:
    curve_txs = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id, Transaction.source_type == SourceType.curve)
        .all()
    )
    bank_txs = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id, Transaction.source_type == SourceType.bank)
        .all()
    )
    out: list[CurveDuplicateCandidateResponse] = []

    for curve_tx in curve_txs:
        for bank_tx in bank_txs:
            result = match_curve_to_bank(curve_tx, bank_tx)
            if result.matched:
                out.append(
                    CurveDuplicateCandidateResponse(
                        confidence=result.confidence,
                        reason=result.reason,
                        curve_transaction=TransactionResponse.model_validate(tx_payload(curve_tx)),
                        bank_transaction=TransactionResponse.model_validate(tx_payload(bank_tx)),
                    )
                )
    return out
