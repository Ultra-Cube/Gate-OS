# API Flow Diagram

> REST and WebSocket request/response flows for the Gate-OS Control API.

## REST API Endpoints

```mermaid
sequenceDiagram
    participant C as Client (curl / Flutter / GTK UI)
    participant MW as Middleware (RateLimit + CorrelationID)
    participant AUTH as TokenAuth
    participant API as FastAPI Router
    participant SO as SwitchOrchestrator
    participant PM as PrometheusRegistry

    Note over C,PM: GET /environments
    C->>MW: GET /environments\nAuthorization: Bearer <token>
    MW->>AUTH: validate token
    AUTH-->>MW: ok
    MW->>API: route
    API-->>C: 200 [{name, category, description}]
    PM->>PM: gateos_api_requests_total++

    Note over C,PM: POST /switch/{env}
    C->>MW: POST /switch/gaming\nAuthorization: Bearer <token>
    MW->>AUTH: validate token
    MW->>MW: check rate limit (60 req/min per IP)
    MW->>API: route
    API->>SO: activate("gaming")
    SO-->>API: SwitchResult
    API-->>C: 200 {status, latency_ms, env}

    Note over C,PM: GET /metrics (Prometheus)
    C->>API: GET /metrics
    API->>PM: format()
    PM-->>API: text/plain metrics
    API-->>C: 200 # HELP gateos_switch_total ...
```

## WebSocket Flow

```mermaid
sequenceDiagram
    participant FL as Flutter App / Browser
    participant WM as ConnectionManager
    participant API as FastAPI /ws/status
    participant SO as SwitchOrchestrator

    FL->>API: WS CONNECT /ws/status
    API->>WM: connect(websocket)
    WM-->>FL: {type:"status", active_env, clients}

    FL->>API: {type:"ping"}
    API-->>FL: {type:"pong", ...echo}

    Note over SO,WM: Switch triggered elsewhere
    SO->>API: broadcast_sync(switch_start_msg)
    API->>WM: broadcast to all
    WM-->>FL: {type:"switch_start", env, correlation_id}

    SO->>API: broadcast_sync(switch_done_msg)
    API->>WM: broadcast to all
    WM-->>FL: {type:"switch_done", env, status, correlation_id}

    FL->>API: WS DISCONNECT
    API->>WM: disconnect(websocket)
```

## Authentication Model

```mermaid
graph LR
    A[Client Request] -->|Authorization: Bearer TOKEN| B{Token Match?}
    B -->|Yes| C[Rate Limit Check]
    B -->|No| D[401 Unauthorized]
    C -->|Under limit| E[Route Handler]
    C -->|Over limit| F[429 Too Many Requests]
    E --> G[Response 2xx]
```

## Error Response Codes

| Code | Scenario |
|------|---------|
| 200 | Success |
| 400 | Invalid environment name or malformed request |
| 401 | Missing or invalid bearer token |
| 404 | Environment not found in manifests |
| 409 | Switch already in progress |
| 429 | Rate limit exceeded |
| 500 | Internal error (logged with correlation_id) |

---
**Last updated:** March 2026 | **By:** Fadhel.SH
