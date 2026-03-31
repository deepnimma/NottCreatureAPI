from __future__ import annotations

from fastapi.testclient import TestClient


def test_health(client: TestClient) -> None:
    resp = client.get("/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "public-api"}


def test_health_no_auth_required(client: TestClient) -> None:
    """Health endpoint should not require authentication."""
    resp = client.get("/v1/health")
    assert resp.status_code == 200
