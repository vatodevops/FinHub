import uuid

from pydantic import BaseModel, Field


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    color: str | None
    icon: str | None = None
    parent_id: uuid.UUID | None = None

    model_config = {"from_attributes": True}


class CreateCategoryRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: str | None = Field(default=None, max_length=20)
    icon: str | None = Field(default=None, max_length=50)
    parent_id: uuid.UUID | None = None


class UpdateCategoryRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = None
    icon: str | None = None
    parent_id: uuid.UUID | None = None


class TransactionCategoryUpdate(BaseModel):
    category_id: uuid.UUID | None = None
