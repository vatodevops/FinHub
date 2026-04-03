import uuid

from pydantic import BaseModel


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    color: str | None

    model_config = {"from_attributes": True}


class TransactionCategoryUpdate(BaseModel):
    category_id: uuid.UUID | None = None
