"""FastAPI app — M1 Foundation + M2 (bids, pipeline, questions).

- Mount prefix ``/api`` (BR-10).
- Lifespan: ``init_db()`` tạo bảng (create_all, không Alembic — BR-09).
- Exception handlers: envelope lỗi ``{error:{code,message,details}}`` (contract §1.3).
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.errors import register_exception_handlers
from app.api.routers import api_router
from app.core.db import init_db
from app.core.logging import setup_logging
from app.core.config import settings

setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Presales Bidding Assistant",
    version=__version__,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "X-Actor", "X-Role", "X-User"],
    allow_credentials=True,
)
register_exception_handlers(app)
app.include_router(api_router, prefix="/api")
