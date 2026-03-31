from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_sets_no_auth(client: TestClient) -> None:
    resp = client.get("/v1/sets")
    assert resp.status_code == 401


def test_list_sets(client: TestClient, valid_api_key: str) -> None:
    resp = client.get("/v1/sets", headers={"X-API-Key": valid_api_key})
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert "pagination" in body
    assert len(body["data"]) == 1
    assert body["data"][0]["id"] == "base1"


def test_get_set(client: TestClient, valid_api_key: str) -> None:
    resp = client.get("/v1/sets/base1", headers={"X-API-Key": valid_api_key})
    assert resp.status_code == 200
    assert resp.json()["id"] == "base1"
    assert resp.json()["name"] == "Base Set"


def test_get_set_not_found(client: TestClient, valid_api_key: str) -> None:
    resp = client.get("/v1/sets/nonexistent", headers={"X-API-Key": valid_api_key})
    assert resp.status_code == 404


def test_list_set_cards(client: TestClient, valid_api_key: str) -> None:
    resp = client.get("/v1/sets/base1/cards", headers={"X-API-Key": valid_api_key})
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert len(body["data"]) == 1
    assert body["data"][0]["id"] == "base1-1"


def test_list_set_cards_no_auth(client: TestClient) -> None:
    resp = client.get("/v1/sets/base1/cards")
    assert resp.status_code == 401
