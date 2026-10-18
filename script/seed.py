import asyncio
import csv
import sys
from pathlib import Path
from datetime import datetime
from sqlalchemy import delete

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from find_doc.db.base import Base
from find_doc.db.session import engine, async_session
from find_doc.db.models import Document
from find_doc.elasticsearch.client import es_client
from find_doc.elasticsearch.index import INDEX_NAME, init_index


async def main(csv_path: str):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_index()

    async with async_session() as session:
        await session.execute(delete(Document))
        await session.commit()
    
    await es_client.delete_by_query(index=INDEX_NAME, body={"query": {"match_all": {}}})

    documents = []
    es_operations = []

    with open(csv_path, "r", encoding="utf-8") as f:
        for idx, row in enumerate(csv.DictReader(f), start=1):
            doc_id = idx
            
            raw_rubrics = row.get("rubrics", "").strip()
            clean_rubrics = raw_rubrics.replace("[", "").replace("]", "").replace("'", "").replace('"', "")
            rubrics = [r.strip() for r in clean_rubrics.replace(";", ",").split(",") if r.strip()]
            
            text = row.get("text", "").strip()
            date_str = row.get("created_date", "").strip()
            
            created_date = None
            if date_str:
                created_date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            documents.append(Document(id=doc_id, rubrics=rubrics, text=text, created_date=created_date))
            
            es_operations.extend([
                {"index": {"_index": INDEX_NAME, "_id": doc_id}},
                {"id": doc_id, "text": text}
            ])

    async with async_session() as session:
        session.add_all(documents)
        await session.commit()

    try:
        if es_operations:
            await es_client.bulk(operations=es_operations, refresh=True)
    finally:
        await es_client.close()

    print(f"Imported {len(documents)} documents.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run python scripts/seed.py <csv_path>")
        sys.exit(1)
    
    asyncio.run(main(sys.argv[1]))
