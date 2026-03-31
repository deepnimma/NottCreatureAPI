from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.limits import load_limits
from app.rate_limit import limiter
from app.routers.cards import router as cards_router
from app.routers.health import router as health_router
from app.routers.keys import router as keys_router
from app.routers.sets import router as sets_router

__all__ = ["app"]


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    load_limits(settings.limits_config_path)
    yield


app = FastAPI(title="NottCreature Public API", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/v1")
app.include_router(sets_router, prefix="/v1")
app.include_router(cards_router, prefix="/v1")
app.include_router(keys_router, prefix="/v1")
