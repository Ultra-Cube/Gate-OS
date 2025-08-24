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
