from contextlib import asynccontextmanager

from fastapi import FastAPI

from find_doc.db.base import Base
from find_doc.db.session import async_session, engine
from find_doc.documents.service import bulk_index_documents
from find_doc.elasticsearch.client import es_client
from find_doc.elasticsearch.index import init_index


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await init_index()

    async with async_session() as db:
        await bulk_index_documents(db)

    yield

    # Shutdown
    await es_client.close()
    await engine.dispose()
