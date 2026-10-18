from fastapi import FastAPI

from find_doc.api import router
from find_doc.core.lifespan import lifespan

app = FastAPI(
    title="Document Search Service",
    description="Поисковик по текстам документов",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}
