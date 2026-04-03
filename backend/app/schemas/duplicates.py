from pydantic import BaseModel

from app.schemas.transactions import TransactionResponse


class CurveDuplicateCandidateResponse(BaseModel):
    confidence: float
    reason: str
    curve_transaction: TransactionResponse
    bank_transaction: TransactionResponse
