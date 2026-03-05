# OpenTelemetry / OTLP Integration

Gate-OS ships a built-in OTLP/HTTP JSON exporter that sends traces and log
signals to any OpenTelemetry-compatible collector (Jaeger, Tempo, SigNoz, etc.)
without requiring the full `opentelemetry-sdk`.

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `GATEOS_OTLP_ENDPOINT` | `http://localhost:4318` | OTLP collector base URL |
| `GATEOS_OTLP_SERVICE` | `gate-os-manager` | Service name in resource attributes |
| `GATEOS_OTLP_TIMEOUT` | `3` | HTTP request timeout (seconds) |
| `GATEOS_OTLP_DISABLE` | (unset) | Set to `1` to silence all exports |

## Quick Start

```python
from gateos_manager.telemetry.otlp import default_exporter

exp = default_exporter()

# Export a log record
exp.export_log("switch.started", attrs={"env": "gaming", "correlation_id": "abc123"})

# Export a trace span
import time
t0 = int(time.time() * 1e9)
# ... do work ...
t1 = int(time.time() * 1e9)
exp.export_span("switch.pipeline", start_ns=t0, end_ns=t1, attrs={"env": "gaming"})

# Batch export
events = [
    {"name": "container.started", "container": "gaming-audio"},
    {"name": "profile.applied", "governor": "performance"},
]
exp.export_batch(events)
```

## Collector Setup (Docker Compose)

```yaml
# docker-compose.observability.yml
services:
  otel-collector:
    image: otel/opentelemetry-collector-contrib:0.97.0
    ports:
      - "4318:4318"   # OTLP HTTP
      - "4317:4317"   # OTLP gRPC (not used by Gate-OS)
    volumes:
      - ./otel-config.yaml:/etc/otelcol/config.yaml

  jaeger:
    image: jaegertracing/all-in-one:1.56
    ports:
      - "16686:16686"  # Jaeger UI
```

Start with:

```bash
docker compose -f docker-compose.observability.yml up -d
export GATEOS_OTLP_ENDPOINT=http://localhost:4318
gateos api
```

Then open [http://localhost:16686](http://localhost:16686) to browse traces.

## Integration with Switch Events

The switch orchestrator emits OTLP spans automatically when
`GATEOS_OTLP_ENDPOINT` is set:

```
switch.pipeline        → root span (full switch duration)
  ├─ services.stop     → stop active environment services
  ├─ profile.apply     → CPU governor + GPU mode
  ├─ containers.start  → podman run for each container
  └─ services.start    → start new environment services
```

## Emitting Custom Events

Use the module-level helper anywhere in your plugin code:

```python
from gateos_manager.telemetry.otlp import default_exporter

def pre_switch(env_name: str, **_kw) -> None:
    default_exporter().export_log(
        "plugin.pre_switch",
        attrs={"env": env_name, "plugin": "my-plugin"},
    )
```
