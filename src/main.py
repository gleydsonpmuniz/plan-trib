from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from sqlalchemy import text

from src.api import apuracao, auth, despesas, documentos, empresas, grupos
from src.config import settings
from src.db import engine

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)
    logger.info("startup", domain=settings.app_domain)
    yield
    await engine.dispose()
    logger.info("shutdown")


app = FastAPI(title="Planejamento Tributário", version="0.1.0", lifespan=lifespan)


@app.get("/api/health")
async def health() -> dict:
    db_ok = False
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass
    return {"status": "ok" if db_ok else "degraded", "db": db_ok, "version": "0.1.0"}


api_prefix = "/api"
app.include_router(auth.router, prefix=api_prefix)
app.include_router(grupos.router, prefix=api_prefix)
app.include_router(empresas.router, prefix=api_prefix)
app.include_router(documentos.router, prefix=api_prefix)
app.include_router(despesas.router, prefix=api_prefix)
app.include_router(apuracao.router, prefix=api_prefix)
