from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from find_doc.db.session import get_db
from find_doc.documents.service import create_document, delete_document
from find_doc.schemas import (
    DeleteResponse,
    DocumentCreate,
    DocumentResponse,
    SearchResponse,
)
from find_doc.search.service import search_documents

router = APIRouter()


@router.post("/documents", response_model=DocumentResponse, status_code=201)
async def add_document(
    doc: DocumentCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_document(db, doc.model_dump())


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    db: AsyncSession = Depends(get_db),
):
    docs = await search_documents(db, q)
    return SearchResponse(total=len(docs), documents=docs)


@router.delete("/documents/{doc_id}", response_model=DeleteResponse)
async def remove_document(
    doc_id: int,
    db: AsyncSession = Depends(get_db),
):
    deleted = await delete_document(db, doc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    return DeleteResponse(id=doc_id, deleted=True)
