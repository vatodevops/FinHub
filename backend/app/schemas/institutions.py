import uuid

from pydantic import BaseModel


class InstitutionResponse(BaseModel):
    id: uuid.UUID
    name: str
    provider: str
    source_type: str

    model_config = {"from_attributes": True}
