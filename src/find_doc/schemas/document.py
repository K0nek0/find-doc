from datetime import datetime

from pydantic import BaseModel


class DocumentCreate(BaseModel):
    id: int
    rubrics: list[str] | None = []
    text: str
    created_date: datetime | None = None


class DocumentResponse(BaseModel):
    id: int
    rubrics: list[str] | None = []
    text: str
    created_date: datetime | None = None

    model_config = {"from_attributes": True}


class SearchResponse(BaseModel):
    total: int
    documents: list[DocumentResponse]


class DeleteResponse(BaseModel):
    id: int
    deleted: bool
