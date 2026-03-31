from __future__ import annotations

from fastapi.testclient import TestClient

# ── Registration ──────────────────────────────────────────────────────────────

def test_register_valid_invite(client: TestClient) -> None:
    resp = client.post("/v1/keys", json={"invite_code": "valid-code-abc", "label": "My Key"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["key"].startswith("ptcg_")
    assert data["prefix"] == data["key"][:8]


def test_register_invalid_invite(client: TestClient) -> None:
    resp = client.post("/v1/keys", json={"invite_code": "does-not-exist"})
    assert resp.status_code == 404


def test_register_used_invite(client: TestClient) -> None:
    resp = client.post("/v1/keys", json={"invite_code": "used-code-xyz"})
    assert resp.status_code == 409


# ── GET /v1/keys/me ───────────────────────────────────────────────────────────

def test_get_my_key(client: TestClient, valid_api_key: str) -> None:
    resp = client.get("/v1/keys/me", headers={"X-API-Key": valid_api_key})
    assert resp.status_code == 200
    data = resp.json()
    assert data["prefix"] == "ptcg_te"
    assert data["tier"] == "standard"
    assert data["label"] == "Test Key"
    assert "created_at" in data


def test_get_my_key_no_auth(client: TestClient) -> None:
    resp = client.get("/v1/keys/me")
    assert resp.status_code == 401


# ── POST /v1/keys/rotate ──────────────────────────────────────────────────────

def test_rotate_key(client: TestClient, valid_api_key: str) -> None:
    resp = client.post("/v1/keys/rotate", headers={"X-API-Key": valid_api_key})
    assert resp.status_code == 200
    data = resp.json()
    assert data["key"].startswith("ptcg_")
    assert data["prefix"] == data["key"][:8]


def test_rotate_key_no_auth(client: TestClient) -> None:
    resp = client.post("/v1/keys/rotate")
    assert resp.status_code == 401


# ── DELETE /v1/keys/me ────────────────────────────────────────────────────────

def test_revoke_key(client: TestClient, valid_api_key: str) -> None:
    resp = client.delete("/v1/keys/me", headers={"X-API-Key": valid_api_key})
    assert resp.status_code == 204


def test_revoke_key_no_auth(client: TestClient) -> None:
    resp = client.delete("/v1/keys/me")
    assert resp.status_code == 401
