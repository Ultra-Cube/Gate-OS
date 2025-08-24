import os
import time
from fastapi.testclient import TestClient
from gateos_manager.api.server import app
from gateos_manager.api import rate_limit as rl


def test_rate_limit_basic_window_reset(monkeypatch):
    client = TestClient(app)
    # Reset buckets to avoid interference from previous tests
    rl._buckets.clear()
    os.environ["GATEOS_API_TOKEN"] = "tok"
    os.environ["GATEOS_API_RATE_LIMIT"] = "2"
    os.environ["GATEOS_API_RATE_WINDOW"] = "1"  # 1 second window
    # First two requests allowed
    for _ in range(2):
        r = client.post("/switch/does-not-exist", headers={"x-token": "tok", "x-client-id": "rltest"})
        # 404 because environment missing means auth/rate ok
        assert r.status_code == 404
    # Third should 429
    r3 = client.post("/switch/does-not-exist", headers={"x-token": "tok", "x-client-id": "rltest"})
    assert r3.status_code == 429
    # Wait for window reset
    time.sleep(1.1)
    r4 = client.post("/switch/does-not-exist", headers={"x-token": "tok", "x-client-id": "rltest"})
    assert r4.status_code == 404
