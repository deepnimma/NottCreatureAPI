from __future__ import annotations

from pydantic import BaseModel

from app.models.card import Legality
from app.models.common import PaginationMeta

__all__ = ["CardSet", "SetListResponse"]


class CardSet(BaseModel):
    id: str
    name: str
    series: str
    printed_total: int
    total: int
    legalities: Legality
    ptcgo_code: str | None = None
    release_date: str
    updated_at: str
    logo_url: str | None = None
    symbol_url: str | None = None


class SetListResponse(BaseModel):
    data: list[CardSet]
    pagination: PaginationMeta
