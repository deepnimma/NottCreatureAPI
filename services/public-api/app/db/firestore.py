from __future__ import annotations

import base64
from typing import Any

from app.config import settings
from app.logging import get_logger

__all__ = ["get_document", "get_firestore", "paginate_collection"]

logger = get_logger(__name__)

_client: Any | None = None


def get_firestore() -> Any:
    global _client
    if _client is None:
        from google.cloud.firestore_v1.async_client import AsyncClient

        _client = AsyncClient(project=settings.google_cloud_project)
    return _client


def _encode_cursor(value: str) -> str:
    return base64.urlsafe_b64encode(value.encode()).decode()


def _decode_cursor(token: str) -> str:
    return base64.urlsafe_b64decode(token.encode()).decode()


async def get_document(db: Any, collection: str, doc_id: str) -> dict[str, Any] | None:
    doc = await db.collection(collection).document(doc_id).get()
    if not doc.exists:
        return None
    data: dict[str, Any] = doc.to_dict() or {}
    data["id"] = doc.id
    return data


async def paginate_collection(
    db: Any,
    collection: str,
    page_size: int,
    page_token: str | None,
    order_by: str,
    direction: str = "ASCENDING",
    filters: list[tuple[str, str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], str | None]:
    coll_ref = db.collection(collection)
    query = coll_ref.order_by(order_by, direction=direction)

    if filters:
        from google.cloud.firestore_v1 import FieldFilter

        for field, op, value in filters:
            query = query.where(filter=FieldFilter(field, op, value))

    if page_token:
        query = query.start_after({order_by: _decode_cursor(page_token)})

    query = query.limit(page_size + 1)

    docs: list[dict[str, Any]] = []
    async for doc in query.stream():
        data: dict[str, Any] = doc.to_dict() or {}
        data["id"] = doc.id
        docs.append(data)

    next_token: str | None = None
    if len(docs) > page_size:
        docs = docs[:page_size]
        next_token = _encode_cursor(str(docs[-1].get(order_by, "")))

    return docs, next_token
