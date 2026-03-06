# Quickstart

Get Gate-OS running in under 5 minutes.

---

## Prerequisites

- Python 3.11+
- Linux (Ubuntu 22.04+ or Fedora 38+ recommended)
- `podman` or `docker` (optional — required only for container environments)
- `systemd` (optional — required for service switching; dry-run mode works without it)

---

## Install

=== "pip (development)"

    ```bash
    git clone https://github.com/Ultra-Cube/Gate-OS.git
    cd Gate-OS
    make setup        # creates venv + installs dev deps
    source .venv/bin/activate
    ```

=== "pipx (user install)"

    ```bash
    pipx install gate-os    # coming soon on PyPI
    ```

---

## 1. Validate a manifest

```bash
# Validate the example gaming environment manifest
gateos validate environments/gaming.yaml
# OK: environments/gaming.yaml
```

If validation fails, the error message contains the schema path and reason:

```
FAIL: environments/gaming.yaml: 'services' is a required property
```

---

## 2. List available environments

```bash
gateos list
```

Output:

```
gaming   (category: gaming)
dev      (category: development)
design   (category: design)
media    (category: media)
```

---

## 3. Switch to an environment

```bash
gateos switch gaming
```

Output:

```
[INFO] Starting switch to: gaming
[INFO] Running pre_switch hooks
[INFO] Stopping services: []
[INFO] Starting services: [steam, pipewire]
[INFO] Containers started: [redis]
[INFO] Running post_switch hooks
[INFO] Switch complete: gaming
```

Gate-OS emits OTLP spans and structured JSON logs for every switch event.

---

## 4. Start the Control API

```bash
gateos api
# Uvicorn running on http://127.0.0.1:8000
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive Swagger UI.

```bash
# Switch environment via REST API
curl -s -X POST http://localhost:8000/switch \
     -H "Authorization: Bearer $GATEOS_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"environment": "dev"}'
```

---

## 5. Check for updates

```bash
gateos check-update
# Latest version: v1.3.0 — https://github.com/Ultra-Cube/Gate-OS/releases/tag/v1.3.0

gateos apply-update --yes
# Downloaded: gate-os_1.3.0_amd64.deb — ready to install
```

---

## Next Steps

- [Configuration reference](configuration.md) — all environment variables
- [Architecture overview](../architecture/overview.md) — how the switch engine works
- [Manifest schema](../architecture/environments.md) — define your own environments
- [CLI reference](../api/control-api.md) — all CLI commands
