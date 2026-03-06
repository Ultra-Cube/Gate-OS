# Configuration Reference

All Gate-OS runtime behaviour is controlled via environment variables. No config file is required.

---

## OTLP / Telemetry

| Variable | Default | Description |
|---|---|---|
| `GATEOS_OTLP_ENDPOINT` | `http://localhost:4318/v1/traces` | OTLP/HTTP endpoint for trace export |
| `GATEOS_OTLP_LOGS_ENDPOINT` | `http://localhost:4318/v1/logs` | OTLP/HTTP endpoint for log export |
| `GATEOS_OTLP_DISABLE` | `""` | Set to `1` to disable all OTLP export (air-gapped) |
| `GATEOS_OTLP_BATCH_SIZE` | `512` | Max spans per export batch |
| `GATEOS_OTLP_TIMEOUT` | `5` | Exporter HTTP timeout in seconds |

---

## Container Runtime

| Variable | Default | Description |
|---|---|---|
| `GATEOS_CONTAINER_RUNTIME` | auto-detect | Force `podman` or `docker` runtime |
| `GATEOS_CONTAINER_DRY_RUN` | `""` | Set to `1` to skip container operations (no runtime required) |
| `GATEOS_CONTAINER_PULL_POLICY` | `missing` | Image pull policy: `always`, `missing`, `never` |

---

## API Server

| Variable | Default | Description |
|---|---|---|
| `GATEOS_API_TOKEN` | (required) | Bearer token for API authentication |
| `GATEOS_API_TOKEN_FILE` | `""` | Path to file containing API token (alternative to env var) |
| `GATEOS_API_HOST` | `127.0.0.1` | API server bind address |
| `GATEOS_API_PORT` | `8000` | API server port |
| `GATEOS_API_RATE_LIMIT` | `60` | Max requests per minute per IP |

---

## OTA Updates

| Variable | Default | Description |
|---|---|---|
| `GATEOS_UPDATE_BASE_URL` | `https://api.github.com/repos/Ultra-Cube/Gate-OS/releases` | GitHub Releases API base URL |
| `GATEOS_UPDATE_DIR` | `/tmp/gateos-updates` | Directory for downloaded update packages |
| `GATEOS_CURRENT_VERSION` | (from package metadata) | Override current version string for update comparison |

---

## Security

| Variable | Default | Description |
|---|---|---|
| `GATEOS_KEY_DIR` | `/etc/gateos/keys` | Directory for Ed25519 signing keys |
| `GATEOS_REQUIRE_SIGNED_MANIFESTS` | `""` | Set to `1` to reject unsigned manifests (v1.3.0) |

---

## Environment Resolution

| Variable | Default | Description |
|---|---|---|
| `GATEOS_MANIFEST_DIR` | `environments/` (relative to CWD) | Directory to scan for YAML manifests |
| `GATEOS_DRY_RUN` | `""` | Set to `1` for full dry-run (no services, no containers, no hardware changes) |

---

## Logging

| Variable | Default | Description |
|---|---|---|
| `GATEOS_LOG_LEVEL` | `INFO` | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `GATEOS_LOG_FORMAT` | `json` | Log format: `json` (structured) or `text` (human-readable) |

---

## Complete Example

```bash
export GATEOS_API_TOKEN="$(openssl rand -hex 32)"
export GATEOS_OTLP_ENDPOINT="http://otel-collector:4318/v1/traces"
export GATEOS_CONTAINER_RUNTIME="podman"
export GATEOS_MANIFEST_DIR="/etc/gateos/environments"
export GATEOS_LOG_LEVEL="DEBUG"

gateos switch gaming
```

---

## See Also
- [Quickstart](quickstart.md)
- [Architecture Overview](../architecture/overview.md)
- [API Reference](../api/control-api.md)
