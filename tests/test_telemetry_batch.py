import os
import time
from pathlib import Path
from gateos_manager.telemetry import emitter


def test_telemetry_batch_queue_and_flush(tmp_path: Path, monkeypatch):
    # Configure batch mode with small batch size & short interval
    os.environ["GATEOS_TELEMETRY_ENABLED"] = "1"
    os.environ["GATEOS_TELEMETRY_BATCH"] = "1"
    os.environ["GATEOS_TELEMETRY_BATCH_INTERVAL"] = "0.2"
    os.environ["GATEOS_TELEMETRY_BATCH_SIZE"] = "5"
    # Use dummy OTLP endpoint (will be ignored network errors suppressed)
    os.environ["GATEOS_TELEMETRY_OTLP_HTTP"] = "http://127.0.0.1:9/otlp"  # unroutable port
    # Emit several events rapidly
    for i in range(7):
        emitter.emit("test.event", idx=i)
    # Explicit flush to drain queue
    emitter.flush()
    # Nothing to assert externally (network suppressed); ensure no exceptions and queue drained
    # Emit again after flush to ensure thread still alive
    emitter.emit("test.event", idx=99)
    emitter.flush()


def test_telemetry_batch_size_threshold(monkeypatch):
    """Ensure batch exporter respects max batch size and leaves remainder until interval elapses.

    We configure a small batch size (5) with a longer interval so that after emitting
    more than 5 events rapidly only the first batch is exported (removed from the queue)
    while the remainder stay queued (since exporter sleeps for the interval before next batch).
    """
    import time
    # Environment configuration
    os.environ["GATEOS_TELEMETRY_ENABLED"] = "1"
    os.environ["GATEOS_TELEMETRY_BATCH"] = "1"
    os.environ["GATEOS_TELEMETRY_BATCH_INTERVAL"] = "2"  # long enough we won't hit second cycle
    os.environ["GATEOS_TELEMETRY_BATCH_SIZE"] = "5"
    os.environ["GATEOS_TELEMETRY_OTLP_HTTP"] = "http://127.0.0.1:9/otlp"  # unroutable
    # Drain any existing queue from prior tests
    if getattr(emitter, "_BATCH_Q", None) is not None:
        try:
            while True:
                emitter._BATCH_Q.get_nowait()
        except Exception:
            pass
    total = 8
    for i in range(total):
        emitter.emit("test.batch.size", idx=i)
    # Allow background thread to pick up first batch
    time.sleep(0.2)
    qsize = emitter._BATCH_Q.qsize() if emitter._BATCH_Q is not None else 0
    # Expect exactly (total - batch_size) items remaining (8 - 5 = 3)
    assert qsize == 3, f"expected 3 remaining queued events, found {qsize}"
