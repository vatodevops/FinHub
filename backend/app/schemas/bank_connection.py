import uuid
from datetime import datetime

from pydantic import BaseModel


class BankConnectionResponse(BaseModel):
    id: uuid.UUID
    provider: str
    requisition_id: str
    reference: str
    institution_external_id: str | None
    institution_name: str | None
    link: str | None
    status: str
    last_synced_at: datetime | None
    error_message: str | None

    model_config = {"from_attributes": True}
