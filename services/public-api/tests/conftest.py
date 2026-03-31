from __future__ import annotations

import copy
import hashlib
import os
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

import pytest

# Must be set before any app module is imported
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")
os.environ.setdefault("LIMITS_CONFIG_PATH", "config/limits.yaml")
os.environ.setdefault("CORS_ALLOWED_ORIGINS", "http://localhost:3000")

from fastapi.testclient import TestClient  # noqa: E402

from app.db.firestore import get_firestore  # noqa: E402
from app.main import app  # noqa: E402

# ── Test keys ────────────────────────────────────────────────────────────────

TEST_API_KEY = "ptcg_test_abc123"
INACTIVE_API_KEY = "ptcg_inactive_xyz"
TEST_KEY_HASH = hashlib.sha256(TEST_API_KEY.encode()).hexdigest()
INACTIVE_KEY_HASH = hashlib.sha256(INACTIVE_API_KEY.encode()).hexdigest()

# ── Test data ─────────────────────────────────────────────────────────────────

_SETS: dict[str, dict[str, Any]] = {
    "base1": {
        "name": "Base Set",
        "series": "Base",
        "printed_total": 102,
        "total": 102,
        "legalities": {"standard": False, "expanded": False, "unlimited": True},
        "ptcgo_code": "BS",
        "release_date": "1999/01/09",
        "updated_at": "2022/09/27",
        "logo_url": None,
        "symbol_url": None,
    }
}

_CARDS: dict[str, dict[str, Any]] = {
    "base1-1": {
        "name": "Alakazam",
        "supertype": "Pokémon",
        "subtypes": ["Stage 2"],
        "hp": 80,
        "types": ["Psychic"],
        "evolves_from": "Kadabra",
        "evolves_to": [],
        "rules": [],
        "abilities": [],
        "attacks": [
            {
                "name": "Damage Swap",
                "cost": ["Psychic"],
                "converted_energy_cost": 1,
                "damage": None,
                "description": "Move damage counters around.",
            }
        ],
        "weaknesses": [{"type": "Psychic", "value": "×2"}],
        "resistances": [],
        "retreat_cost": ["Colorless", "Colorless", "Colorless"],
        "converted_retreat_cost": 3,
        "set_id": "base1",
        "number": "1",
        "artist": "Ken Sugimori",
        "rarity": "Rare Holo",
        "flavor_text": "Its brain can outperform a supercomputer.",
        "national_pokedex_numbers": [65],
        "legalities": {"standard": False, "expanded": False, "unlimited": True},
        "image_url": "https://example.com/alakazam.png",
        "translations": {
            "fr": {"name": "Alakazam (FR)", "description": None, "flavor_text": None}
        },
    }
}

_API_KEYS: dict[str, dict[str, Any]] = {
    TEST_KEY_HASH: {
        "prefix": "ptcg_te",
        "tier": "standard",
        "active": True,
        "label": "Test Key",
        "created_at": datetime(2025, 1, 1, tzinfo=UTC),
        "last_used_at": None,
    },
    INACTIVE_KEY_HASH: {
        "prefix": "ptcg_in",
        "tier": "standard",
        "active": False,
        "label": None,
        "created_at": datetime(2025, 1, 1, tzinfo=UTC),
        "last_used_at": None,
    },
}

_INVITE_CODES: dict[str, dict[str, Any]] = {
    "valid-code-abc": {"used": False},
    "used-code-xyz": {"used": True},
}

# ── Fake Firestore ────────────────────────────────────────────────────────────


class _FakeDoc:
    def __init__(self, doc_id: str, data: dict[str, Any] | None) -> None:
        self.id = doc_id
        self._data = data
        self.exists = data is not None

    def to_dict(self) -> dict[str, Any] | None:
        return dict(self._data) if self._data else None


class _FakeDocRef:
    def __init__(self, doc_id: str, collection_docs: dict[str, dict[str, Any]]) -> None:
        self._doc_id = doc_id
        self._coll = collection_docs

    async def get(self) -> _FakeDoc:
        return _FakeDoc(self._doc_id, self._coll.get(self._doc_id))

    async def update(self, updates: dict[str, Any]) -> None:
        if self._doc_id in self._coll:
            self._coll[self._doc_id].update(updates)

    async def set(self, data: dict[str, Any]) -> None:
        self._coll[self._doc_id] = data


class _FakeQuery:
    def __init__(self, docs: list[tuple[str, dict[str, Any]]]) -> None:
        self._docs = list(docs)
        self._limit_val: int | None = None

    def order_by(self, field: str, direction: Any = None) -> _FakeQuery:
        reverse = str(direction).upper() == "DESCENDING"
        sorted_docs = sorted(
            self._docs, key=lambda x: str(x[1].get(field, "")), reverse=reverse
        )
        q = _FakeQuery(sorted_docs)
        q._limit_val = self._limit_val
        return q

    def where(self, field: str = "", op: str = "==", value: Any = None, **kwargs: Any) -> _FakeQuery:
        # Support both old positional and new filter= kwarg style
        if "filter" in kwargs:
            f = kwargs["filter"]
            field, op, value = f.field_path, f.op_string, f.value  # type: ignore[attr-defined]
        if op == "==":
            filtered = [(doc_id, data) for doc_id, data in self._docs if data.get(field) == value]
        else:
            filtered = self._docs
        q = _FakeQuery(filtered)
        q._limit_val = self._limit_val
        return q

    def start_after(self, cursor: Any) -> _FakeQuery:
        return self

    def limit(self, n: int) -> _FakeQuery:
        q = _FakeQuery(self._docs)
        q._limit_val = n
        return q

    async def stream(self) -> AsyncGenerator[_FakeDoc, None]:
        docs = self._docs
        if self._limit_val is not None:
            docs = docs[: self._limit_val]
        for doc_id, data in docs:
            yield _FakeDoc(doc_id, data)


class _FakeCollection:
    def __init__(self, docs: dict[str, dict[str, Any]]) -> None:
        self._docs = docs

    def document(self, doc_id: str) -> _FakeDocRef:
        return _FakeDocRef(doc_id, self._docs)

    def order_by(self, field: str, direction: Any = None) -> _FakeQuery:
        return _FakeQuery(list(self._docs.items())).order_by(field, direction)

    def where(self, **kwargs: Any) -> _FakeQuery:
        return _FakeQuery(list(self._docs.items())).where(**kwargs)


class FakeFirestore:
    def __init__(self, data: dict[str, dict[str, dict[str, Any]]]) -> None:
        self._data = data

    def collection(self, name: str) -> _FakeCollection:
        return _FakeCollection(self._data.get(name, {}))


# ── Wire overrides ────────────────────────────────────────────────────────────

_INITIAL_DB_DATA: dict[str, dict[str, dict[str, Any]]] = {
    "api_keys": _API_KEYS,
    "sets": _SETS,
    "cards": _CARDS,
    "invite_codes": _INVITE_CODES,
}


def _make_fake_db() -> FakeFirestore:
    return FakeFirestore(copy.deepcopy(_INITIAL_DB_DATA))


app.dependency_overrides[get_firestore] = _make_fake_db

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def client() -> TestClient:  # type: ignore[return]
    with TestClient(app) as c:
        yield c  # type: ignore[misc]


@pytest.fixture
def valid_api_key() -> str:
    return TEST_API_KEY


@pytest.fixture
def inactive_api_key() -> str:
    return INACTIVE_API_KEY
