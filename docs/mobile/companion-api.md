# Gate-OS Mobile Companion

## Overview

The Gate-OS Mobile Companion lets you monitor and control your Gate-OS installation from an Android device over your local network.

**Features:**
- Real-time environment status via WebSocket
- Remote environment switching with one tap
- Push-style notifications when environment changes
- API token authentication

---

## Architecture

```
Android App (Flutter)
       │
       │  WebSocket  ws://<gate-os-host>:8088/ws/status
       │  REST        http://<gate-os-host>:8088/switch/{env}
       ▼
Gate-OS Control API (FastAPI, port 8088)
       │
       ▼
Environment Orchestrator (systemd + podman)
```

---

## WebSocket API

### Endpoint

```
ws://<host>:8088/ws/status
```

Authentication is not currently required for WebSocket connections (they run on the same trusted LAN).

### Message Types

All messages are JSON objects with this shape:

```json
{
  "type": "status",
  "active_env": "gaming",
  "timestamp": "2026-03-05T18:00:00+00:00",
  "payload": {}
}
```

| `type`        | When sent                               | Notable `payload` fields |
|---------------|-----------------------------------------|--------------------------|
| `status`      | On initial connect                      | `info`, `clients` count  |
| `switch_start`| When a switch is initiated via API      | `environment`, `correlation_id` |
| `switch_done` | After a switch completes                | `status`, `correlation_id` |
| `pong`        | In reply to any client message          | Echo of received message |
| `error`       | On internal error                       | `detail`                 |

### Subscribing (JavaScript example)

```javascript
const ws = new WebSocket("ws://gate-os.local:8088/ws/status");

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log(msg.type, msg.active_env);
};

// Keep alive
setInterval(() => ws.send(JSON.stringify({ type: "ping" })), 30000);
```

---

## REST: Remote Switch

Trigger an environment switch from the mobile app:

```http
POST /switch/{env_name}
Host: gate-os.local:8088
x-token: <your-api-token>
```

**Response:**
```json
{
  "status": "success",
  "environment": "gaming",
  "correlation_id": "abc123"
}
```

All connected WebSocket clients receive a `switch_done` message within ~100 ms of the switch completing.

---

## Flutter App Scaffold

A minimal Flutter Android app skeleton is available in `mobile/` (scaffold only — not production ready).

### Running the scaffold

```bash
cd mobile/gate_os_companion
flutter pub get
flutter run
```

### Required Flutter packages

```yaml
dependencies:
  flutter:
    sdk: flutter
  web_socket_channel: ^2.4.0
  http: ^1.2.0
  provider: ^6.1.0
```

---

## Security Considerations

- The WebSocket endpoint and REST API are bound to `127.0.0.1` by default. To allow remote access, bind to `0.0.0.0` and use a reverse proxy with TLS (nginx / Caddy).
- Always use the `x-token` header for `POST /switch` — never expose the token in a QR code or unencrypted channel.
- Mobile app should store the API token in Android Keystore, not shared preferences.

---

## Roadmap

| Version | Feature |
|---------|---------|
| v0.5.0  | WebSocket endpoint + REST switch (current) |
| v0.6.0  | Flutter companion app (basic switch UI) |
| v0.7.0  | Push notifications (FCM) on environment change |
| v1.0.0  | Biometric auth, environment scheduling, battery saver mode |
