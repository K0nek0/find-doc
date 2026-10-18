from sqlalchemy.ext.asyncio import AsyncSession

from find_doc.documents.repository import DocumentRepository
from find_doc.elasticsearch.client import es_client
from find_doc.elasticsearch.index import INDEX_NAME


async def search_documents(session: AsyncSession, query: str, limit: int = 20):
    es_response = await es_client.search(
        index=INDEX_NAME,
        body={
            "query": {"match": {"text": query}},
            "size": limit,
        },
    )

    hits = es_response["hits"]["hits"]
    if not hits:
        return []

    doc_ids = [hit["_source"]["id"] for hit in hits]

    repo = DocumentRepository(session)
    return await repo.get_by_ids(doc_ids, limit=limit)
