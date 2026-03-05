"""Phase 2.5: Switch latency performance benchmark.

Measures end-to-end wall-clock time of perform_switch() in dry-run mode
(no real podman/systemctl calls).  Target: < 3 s for a typical 3-container
manifest.  Results are logged to stdout so they appear in CI.

This test is tagged with @pytest.mark.benchmark so it can be filtered with:
  pytest tests/test_perf_switch_latency.py -v
"""
from __future__ import annotations

import os
import time
import json
import tempfile
import pytest

# Ensure dry-run for all components during the benchmark
os.environ['GATEOS_CONTAINER_DRY_RUN'] = '1'
os.environ['GATEOS_PROFILE_DRY_RUN'] = '1'

from gateos_manager.switch.orchestrator import perform_switch  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_manifest(tmp_path: str, n_containers: int) -> str:
    manifest = {
        "apiVersion": "gateos.ultracube.v1alpha1",
        "kind": "Environment",
        "metadata": {"name": "perf-bench"},
        "spec": {
            "profile": {"category": "gaming", "performance": {"cpuGovernor": "performance"}},
            "services": [
                {"name": f"svc-{i}", "action": "start", "required": False}
                for i in range(n_containers)
            ],
            "containers": [
                {"name": f"ctr-{i}", "image": f"busybox:{i}"}
                for i in range(n_containers)
            ],
        },
    }
    path = os.path.join(tmp_path, "perf-bench.json")
    with open(path, "w") as f:
        json.dump(manifest, f)
    return path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.benchmark
def test_switch_latency_single_container(tmp_path):
    """1 container, 1 service — must complete well under 3 s."""
    path = _write_manifest(str(tmp_path), n_containers=1)
    start = time.perf_counter()
    perform_switch(path)
    elapsed = time.perf_counter() - start
    print(f"\n[perf] 1-container switch: {elapsed*1000:.1f} ms")
    assert elapsed < 3.0, f"Switch took {elapsed:.2f}s — exceeded 3 s budget"


@pytest.mark.benchmark
def test_switch_latency_three_containers(tmp_path):
    """3 containers, 3 services — target < 3 s."""
    path = _write_manifest(str(tmp_path), n_containers=3)
    start = time.perf_counter()
    perform_switch(path)
    elapsed = time.perf_counter() - start
    print(f"\n[perf] 3-container switch: {elapsed*1000:.1f} ms")
    assert elapsed < 3.0, f"Switch took {elapsed:.2f}s — exceeded 3 s budget"


@pytest.mark.benchmark
def test_switch_latency_ten_containers(tmp_path):
    """10 containers, 10 services — still must complete in < 3 s in dry-run."""
    path = _write_manifest(str(tmp_path), n_containers=10)
    start = time.perf_counter()
    perform_switch(path)
    elapsed = time.perf_counter() - start
    print(f"\n[perf] 10-container switch: {elapsed*1000:.1f} ms")
    assert elapsed < 3.0, f"Switch took {elapsed:.2f}s — exceeded 3 s budget"


@pytest.mark.benchmark
def test_repeated_switch_stability(tmp_path):
    """Run the same 3-container switch 10× to detect memory/latency creep.

    No single run should exceed 3 s and total must be < 5 s.
    """
    path = _write_manifest(str(tmp_path), n_containers=3)
    times: list[float] = []
    for _ in range(10):
        start = time.perf_counter()
        perform_switch(path)
        times.append(time.perf_counter() - start)

    worst = max(times)
    total = sum(times)
    avg   = total / len(times)
    print(
        f"\n[perf] 10× 3-container switch  avg={avg*1000:.1f}ms  "
        f"worst={worst*1000:.1f}ms  total={total*1000:.0f}ms"
    )
    assert worst < 3.0, f"Worst run {worst:.2f}s exceeded 3 s budget"
    assert total < 5.0, f"Total {total:.2f}s over 10 runs exceeded 5 s budget"
