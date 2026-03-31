from __future__ import annotations

from pydantic import BaseModel

__all__ = ["ErrorResponse", "PaginationMeta"]


class PaginationMeta(BaseModel):
    page_size: int
    next_page_token: str | None = None
    total_count: int | None = None


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
