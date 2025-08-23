import pytest
from pathlib import Path

from fastapi.testclient import TestClient

from gateos_manager.api.server import app, _load_all

SCHEMA = Path("docs/architecture/schemas/environment-manifest.schema.yaml")


@pytest.fixture(scope="module", autouse=True)
def load_env_cache():
    _load_all(SCHEMA)


def test_list_environments_endpoint():
    client = TestClient(app)
    resp = client.get("/environments")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_environment_404():
    client = TestClient(app)
    resp = client.get("/environments/does-not-exist")
    assert resp.status_code == 404


def test_switch_environment_auth_disabled_allows():
    client = TestClient(app)
    envs = client.get("/environments").json()
    if not envs:
        pytest.skip("No example environments present")
    name = envs[0]["name"]
    resp = client.post(f"/switch/{name}")
    assert resp.status_code == 200
    assert resp.json()["environment"] == name


def test_switch_environment_auth_enabled():
    client = TestClient(app)
    envs = client.get("/environments").json()
    if not envs:
        pytest.skip("No example environments present")
    name = envs[0]["name"]
    # Simulate enabling auth by setting token via env monkeypatch
    token = "secret123"
    # FastAPI TestClient allows environ override via context manager
    import os
    os.environ["GATEOS_API_TOKEN"] = token
    resp_fail = client.post(f"/switch/{name}", headers={"x-token": "wrong"})
    assert resp_fail.status_code == 401
    resp_ok = client.post(f"/switch/{name}", headers={"x-token": token})
    assert resp_ok.status_code == 200


def test_rate_limit_enforced(monkeypatch):
    client = TestClient(app)
    envs = client.get("/environments").json()
    if not envs:
        pytest.skip("No example environments present")
    name = envs[0]["name"]
    import os
    os.environ["GATEOS_API_TOKEN"] = "rtok"
    os.environ["GATEOS_API_RATE_LIMIT"] = "2"
    os.environ["GATEOS_API_RATE_WINDOW"] = "60"
    # two allowed
    for _ in range(2):
        r = client.post(f"/switch/{name}", headers={"x-token": "rtok", "x-client-id": "tester"})
        assert r.status_code == 200
    # third should 429
    r3 = client.post(f"/switch/{name}", headers={"x-token": "rtok", "x-client-id": "tester"})
    assert r3.status_code == 429
