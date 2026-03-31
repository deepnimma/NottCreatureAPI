from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.requests import Request

from app.auth import AuthedKey, require_api_key
from app.db.firestore import get_document, get_firestore, paginate_collection
from app.models import CardListResponse, CardSet, CardSummary, PaginationMeta, SetListResponse
from app.rate_limit import limiter, rpm_limit

__all__ = ["router"]

router = APIRouter(tags=["sets"])

_DEFAULT_PAGE_SIZE = 20


@router.get("/sets", response_model=SetListResponse)
@limiter.limit(rpm_limit)  # type: ignore[untyped-decorator]
async def list_sets(
    request: Request,
    authed_key: Annotated[AuthedKey, Depends(require_api_key)],
    db: Annotated[Any, Depends(get_firestore)],
    page_size: int = Query(default=_DEFAULT_PAGE_SIZE, ge=1, le=100),
    page_token: str | None = Query(default=None),
) -> SetListResponse:
    docs, next_token = await paginate_collection(
        db,
        "sets",
        page_size=page_size,
        page_token=page_token,
        order_by="release_date",
        direction="DESCENDING",
    )
    return SetListResponse(
        data=[CardSet(**doc) for doc in docs],
        pagination=PaginationMeta(page_size=page_size, next_page_token=next_token),
    )


@router.get("/sets/{set_id}", response_model=CardSet)
@limiter.limit(rpm_limit)  # type: ignore[untyped-decorator]
async def get_set(
    request: Request,
    set_id: str,
    authed_key: Annotated[AuthedKey, Depends(require_api_key)],
    db: Annotated[Any, Depends(get_firestore)],
) -> CardSet:
    doc = await get_document(db, "sets", set_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Set not found")
    return CardSet(**doc)


@router.get("/sets/{set_id}/cards", response_model=CardListResponse)
@limiter.limit(rpm_limit)  # type: ignore[untyped-decorator]
async def list_set_cards(
    request: Request,
    set_id: str,
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
        filters=[("set_id", "==", set_id)],
    )
    return CardListResponse(
        data=[CardSummary(**doc) for doc in docs],
        pagination=PaginationMeta(page_size=page_size, next_page_token=next_token),
    )
