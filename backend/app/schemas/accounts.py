import uuid

from pydantic import BaseModel


class AccountResponse(BaseModel):
    id: uuid.UUID
    institution_id: uuid.UUID
    name: str
    iban_masked: str | None
    currency: str
    kind: str
    is_active: bool

    model_config = {"from_attributes": True}
