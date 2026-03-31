from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_cards_no_auth(client: TestClient) -> None:
    resp = client.get("/v1/cards")
    assert resp.status_code == 401


def test_list_cards(client: TestClient, valid_api_key: str) -> None:
    resp = client.get("/v1/cards", headers={"X-API-Key": valid_api_key})
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body
    assert "pagination" in body
    assert len(body["data"]) == 1


def test_get_card(client: TestClient, valid_api_key: str) -> None:
    resp = client.get("/v1/cards/base1-1", headers={"X-API-Key": valid_api_key})
    assert resp.status_code == 200
    assert resp.json()["id"] == "base1-1"
    assert resp.json()["name"] == "Alakazam"


def test_get_card_with_lang(client: TestClient, valid_api_key: str) -> None:
    resp = client.get("/v1/cards/base1-1?lang=fr", headers={"X-API-Key": valid_api_key})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Alakazam (FR)"


def test_get_card_not_found(client: TestClient, valid_api_key: str) -> None:
    resp = client.get("/v1/cards/nonexistent", headers={"X-API-Key": valid_api_key})
    assert resp.status_code == 404


def test_inactive_key(client: TestClient, inactive_api_key: str) -> None:
    resp = client.get("/v1/cards", headers={"X-API-Key": inactive_api_key})
    assert resp.status_code == 403
