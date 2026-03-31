from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.requests import Request

from app.auth import AuthedKey, require_api_key
from app.db.firestore import get_document, get_firestore, paginate_collection
from app.models import Card, CardListResponse, CardSummary, PaginationMeta
from app.rate_limit import limiter, rpm_limit

__all__ = ["router"]

router = APIRouter(tags=["cards"])

_DEFAULT_PAGE_SIZE = 20
_TRANSLATABLE_FIELDS = ("name", "flavor_text")


@router.get("/cards", response_model=CardListResponse)
@limiter.limit(rpm_limit)  # type: ignore[untyped-decorator]
async def list_cards(
    request: Request,
    authed_key: Annotated[AuthedKey, Depends(require_api_key)],
    db: Annotated[Any, Depends(get_firestore)],
    page_size: int = Query(default=_DEFAULT_PAGE_SIZE, ge=1, le=100),
    page_token: str | None = Query(default=None),
) -> CardListResponse:
    docs, next_token = await paginate_collection(
        db,
        "cards",
        page_size=page_size,
        page_token=page_token,
        order_by="number",
        direction="ASCENDING",
    )
    return CardListResponse(
        data=[CardSummary(**doc) for doc in docs],
        pagination=PaginationMeta(page_size=page_size, next_page_token=next_token),
    )


@router.get("/cards/{card_id}", response_model=Card)
@limiter.limit(rpm_limit)  # type: ignore[untyped-decorator]
async def get_card(
    request: Request,
    card_id: str,
    authed_key: Annotated[AuthedKey, Depends(require_api_key)],
    db: Annotated[Any, Depends(get_firestore)],
    lang: str | None = Query(default=None),
) -> Card:
    doc = await get_document(db, "cards", card_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Card not found")

    if lang:
        translations: dict[str, Any] = doc.get("translations", {})
        t: dict[str, Any] = translations.get(lang, {})
        for field in _TRANSLATABLE_FIELDS:
            if t.get(field) is not None:
                doc[field] = t[field]

    return Card(**doc)
