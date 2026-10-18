import pytest


@pytest.mark.asyncio
async def test_add_and_search_document(client):
    doc = {
        "id": 1,
        "rubrics": ["tech", "python"],
        "text": "FastAPI это современный фреймворк для создания API на Python",
        "created_date": "2026-10-14T10:00:00Z",
    }
    resp = await client.post("/documents", json=doc)
    assert resp.status_code == 201
    assert resp.json()["id"] == 1

    search_resp = await client.get("/search", params={"q": "FastAPI"})
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert data["total"] >= 1
    assert any(d["id"] == 1 for d in data["documents"])


@pytest.mark.asyncio
async def test_search_returns_top_20_sorted_by_date(client):
    for i in range(25):
        doc = {
            "id": i + 1,
            "rubrics": [],
            "text": "тестовый документ номер " + str(i),
            "created_date": f"2026-01-{(i % 28) + 1:02d}T10:00:00Z",
        }
        await client.post("/documents", json=doc)

    resp = await client.get("/search", params={"q": "тестовый"})
    assert resp.status_code == 200
    docs = resp.json()["documents"]
    assert len(docs) <= 20


@pytest.mark.asyncio
async def test_delete_document(client):
    doc = {"id": 100, "rubrics": [], "text": "удаляемый документ"}
    await client.post("/documents", json=doc)

    resp = await client.delete("/documents/100")
    assert resp.status_code == 200
    assert resp.json()["deleted"] is True

    search_resp = await client.get("/search", params={"q": "удаляемый"})
    docs = search_resp.json()["documents"]
    assert not any(d["id"] == 100 for d in docs)


@pytest.mark.asyncio
async def test_delete_nonexistent(client):
    resp = await client.delete("/documents/9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_search_empty_query(client):
    resp = await client.get("/search", params={"q": ""})
    assert resp.status_code == 422
