import os
from pathlib import Path

from fastapi.testclient import TestClient

from gateos_manager.api.server import app


def test_auth_disabled_allows_without_token_header():
    client = TestClient(app)
    # Ensure no token configured
    os.environ.pop("GATEOS_API_TOKEN", None)
    os.environ.pop("GATEOS_API_TOKEN_FILE", None)
    resp = client.get("/environments")
    assert resp.status_code == 200


def test_auth_env_token_rejects_wrong_header():
    client = TestClient(app)
    os.environ["GATEOS_API_TOKEN"] = "envtok"
    r = client.post("/switch/does-not-exist", headers={"x-token": "wrong"})
    # 401 should occur before 404 (auth check first)
    assert r.status_code == 401


def test_auth_file_token_precedence(tmp_path: Path):
    client = TestClient(app)
    # Disable/clear rate limiting so repeated 401/404 attempts don't trigger 429
    os.environ.pop("GATEOS_API_RATE_LIMIT", None)
    os.environ.pop("GATEOS_API_RATE_WINDOW", None)
    # Set env token AND file token; file token should be used because loader checks file first
    os.environ["GATEOS_API_TOKEN"] = "envtok"
    token_file = tmp_path / "token.txt"
    token_file.write_text("filetok\n", encoding="utf-8")
    os.environ["GATEOS_API_TOKEN_FILE"] = str(token_file)
    # Wrong header (env token) should fail
    r_bad = client.post("/switch/does-not-exist", headers={"x-token": "envtok"})
    assert r_bad.status_code == 401
    # Correct header (file token) proceeds to 404 (since environment missing)
    r_ok = client.post("/switch/does-not-exist", headers={"x-token": "filetok"})
    assert r_ok.status_code == 404


def test_auth_file_missing_fallback_to_env(tmp_path: Path):
    client = TestClient(app)
    os.environ.pop("GATEOS_API_RATE_LIMIT", None)
    os.environ.pop("GATEOS_API_RATE_WINDOW", None)
    os.environ["GATEOS_API_TOKEN"] = "abc123"
    # Point file var to non-existent path -> loader should ignore and use env token
    os.environ["GATEOS_API_TOKEN_FILE"] = str(tmp_path / "nope.txt")
    r_fail = client.post("/switch/does-not-exist", headers={"x-token": "wrong"})
    assert r_fail.status_code == 401
    r_env = client.post("/switch/does-not-exist", headers={"x-token": "abc123"})
    assert r_env.status_code == 404
