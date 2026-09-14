from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import init_db
from .routes.documents import router as documents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Fletchers Document Processing API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(documents_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}