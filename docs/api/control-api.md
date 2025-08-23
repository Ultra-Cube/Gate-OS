# Control API (Mobile / Companion)

The control API offers local programmatic access for listing environments and triggering switches.

## Endpoints (v0 Draft)

| Method | Path | Description |
|--------|------|-------------|
| GET | /environments | List environment names & categories |
| GET | /environments/{name} | Get manifest details |
| POST | /switch/{name} | Request environment switch (stub) |

### Response Models

- `GET /environments`: `[ { name, category } ]`
- `POST /switch/{name}`: `{ status, environment, correlation_id }`

## Security (Planned)

- Localhost binding by default.
- Token auth & pairing (QR) for remote LAN usage.
- Rate limiting for switch requests.

### Current Minimal Auth & Rate Limiting (Implemented Draft)

- Auth: Provide header `x-token` matching either `GATEOS_API_TOKEN` env var or first line of
	file at `GATEOS_API_TOKEN_FILE`. If neither set, auth disabled.
- Rate Limit: Optional in-memory bucket when `GATEOS_API_RATE_LIMIT` is set (requests per
	`GATEOS_API_RATE_WINDOW` seconds, default 60). Exceeding returns HTTP 429.
- Client Identification: Optional `x-client-id` header used as rate limiting key; defaults to `anon`.

### Telemetry

- When `GATEOS_TELEMETRY_ENABLED=1`, switch events emit JSON lines with fields: `ts`, `event`, `environment`, `status`.

### Token Generation

Generate a token:

```bash
gateos gen-token --length 40 > api.token
export GATEOS_API_TOKEN_FILE=api.token
```

## Mobile App Concept

- Flutter client for portability (Android flagship; desktop companion later).
- Real-time status via websocket (future endpoint).

---
**Date:** Aug 2025 | **By:** Fadhel.SH | **Company:** Ultra-Cube Tech
