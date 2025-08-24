# Control API (Mobile / Companion)

The control API offers local programmatic access for listing environments and triggering switches.


## Endpoints (OpenAPI)

| Method | Path | Description |
|--------|------|-------------|
| GET | /environments | List environment names & categories |
| GET | /environments/{name} | Get manifest details |
| POST | /switch/{name} | Request environment switch (token required) |


### Response Models

- `GET /environments`: `[ { name, category } ]`
- `POST /switch/{name}`: `{ status, environment, correlation_id }`


## Security & Auth (OpenAPI)

- All protected endpoints require `x-token` header (APIKey in header, see OpenAPI `/docs`).
- Rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`.
- Client Identification: Optional `x-client-id` header used as rate limiting key; defaults to `anon`.


## Telemetry & Logging

- Telemetry events: set `GATEOS_TELEMETRY_ENABLED=1` (and optionally `GATEOS_TELEMETRY_FILE=...`).
- Structured logs: JSON lines with correlation IDs, log level via `GATEOS_LOG_LEVEL`.


## Token Generation

Generate a token:

```bash
gateos gen-token --length 40 > api.token
export GATEOS_API_TOKEN_FILE=api.token
```


## Sample OpenAPI Usage

```python
import requests
resp = requests.post(
	"http://localhost:8088/switch/dev",
	headers={"x-token": "YOUR_TOKEN"}
)
print(resp.json())
```

## Plugin System

- Plugins can register for `pre_switch` and `post_switch` hooks. See `examples/plugins/sample_plugin.py`.

## Container Manager

- Container orchestration is abstracted via `gateos_manager.containers.manager.ContainerManager` (stub).

## Mobile App Concept

- Flutter client for portability (Android flagship; desktop companion later).
- Real-time status via websocket (future endpoint).

---
**Date:** Aug 2025 | **By:** Fadhel.SH | **Company:** Ultra-Cube Tech
