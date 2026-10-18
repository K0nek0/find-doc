import contextlib

from sqlalchemy.ext.asyncio import AsyncSession

from find_doc.db.models import Document
from find_doc.documents.repository import DocumentRepository
from find_doc.elasticsearch.client import es_client
from find_doc.elasticsearch.index import INDEX_NAME


async def create_document(session: AsyncSession, doc_data: dict) -> Document:
    repo = DocumentRepository(session)
    document = Document(
        id=doc_data["id"],
        rubrics=doc_data.get("rubrics", []),
        text=doc_data["text"],
        created_date=doc_data.get("created_date"),
    )
    document = await repo.create(document)

    await es_client.index(
        index=INDEX_NAME,
        id=document.id,
        document={"id": document.id, "text": document.text},
        refresh=True,
    )
    return document


async def delete_document(session: AsyncSession, doc_id: int) -> bool:
    repo = DocumentRepository(session)
    doc = await repo.get_by_id(doc_id)
    if not doc:
        return False

    await repo.delete(doc_id)

    with contextlib.suppress(Exception):
        await es_client.delete(index=INDEX_NAME, id=doc_id)

    return True


async def bulk_index_documents(session: AsyncSession):
    repo = DocumentRepository(session)
    documents = await repo.get_all()

    operations = []
    for doc in documents:
        operations.append({"index": {"_index": INDEX_NAME, "_id": doc.id}})
        operations.append({"id": doc.id, "text": doc.text})

    if operations:
        await es_client.bulk(body=operations)
