from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from find_doc.db.base import Base
from find_doc.db.session import get_db
from find_doc.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestSession() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Имитация индекса Elasticsearch в памяти (изолирована для каждого теста)
    mock_es_index = {}

    async def mock_index_func(index, id, document, refresh=None):
        mock_es_index[id] = document

    async def mock_search_func(index, body):
        query = body["query"]["match"]["text"].lower()
        hits = []
        for doc_id, doc in mock_es_index.items():
            if query in doc["text"].lower():
                hits.append({"_source": {"id": doc_id}})
        return {"hits": {"hits": hits}}

    async def mock_delete_func(index, id):
        mock_es_index.pop(id, None)

    async def mock_exists_func(index):
        return True  # Индекс всегда "существует" в тестах

    async def mock_bulk_func(operations, refresh=None):
        pass

    # ВАЖНО: Патчим es_client во ВСЕХ модулях, где он импортируется и используется!
    modules_to_patch = [
        "find_doc.documents.service.es_client",
        "find_doc.search.service.es_client",
        "find_doc.core.lifespan.es_client",
    ]

    patches = []
    for module_path in modules_to_patch:
        p = patch(module_path)
        mock_es = p.start()
        mock_es.index = AsyncMock(side_effect=mock_index_func)
        mock_es.search = AsyncMock(side_effect=mock_search_func)
        mock_es.delete = AsyncMock(side_effect=mock_delete_func)
        mock_es.indices.exists = AsyncMock(side_effect=mock_exists_func)
        mock_es.bulk = AsyncMock(side_effect=mock_bulk_func)
        patches.append(p)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # Очистка: останавливаем все патчи и снимаем переопределения
    for p in patches:
        p.stop()
    app.dependency_overrides.clear()
