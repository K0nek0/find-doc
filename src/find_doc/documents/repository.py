from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from find_doc.db.models import Document


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def get_by_id(self, doc_id: int) -> Document | None:
        return await self.session.get(Document, doc_id)

    async def delete(self, doc_id: int) -> bool:
        result = await self.session.execute(
            delete(Document).where(Document.id == doc_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def get_by_ids(self, doc_ids: list[int], limit: int = 20):
        result = await self.session.execute(
            select(Document)
            .where(Document.id.in_(doc_ids))
            .order_by(Document.created_date.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_all(self):
        result = await self.session.execute(select(Document))
        return result.scalars().all()
