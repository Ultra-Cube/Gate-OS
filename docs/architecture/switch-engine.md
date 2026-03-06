# Switch Engine

The **switch engine** (`gateos_manager/orchestrator.py`) is the core of Gate-OS. It executes a deterministic, transactional pipeline to transition the system from one environment to another — with automatic rollback on failure.

---

## Pipeline Overview

```
switch_environment(name)
         │
         ▼
   1. Load Manifest
         │
         ▼
   2. Validate Manifest (JSON Schema)
         │
         ▼
   3. Run pre_switch hooks (plugins + manifest hooks)
         │
         ▼
   4. Stop Services (current environment optional services)
         │
         ▼
   5. Apply Hardware Profile (CPU governor, GPU power mode, NIC priority)
         │
         ▼
   6. Apply Security Policy (isolation level, capability allowlist)
         │
         ▼
   7. Start Services (required → abort on failure; optional → warn on failure)
         │
         ▼
   8. Start Containers (podman or docker)
         │
         ▼
   9. Run post_switch hooks (plugins + manifest hooks)
         │
         ▼
  10. Emit telemetry (OTLP span: switch.pipeline, Prometheus counters)
         │
         ▼
      DONE ✅
```

If any **required** step fails, the rollback pipeline runs immediately.

---

## Rollback Pipeline

On failure, the switch engine:

1. Stops any containers that were started in this switch
2. Restores the previous hardware profile
3. Restarts any services that were stopped in this switch
4. Runs `shutdown` plugin hooks
5. Emits a `switch.error` telemetry event with the failure reason

```python
except SwitchError as e:
    orchestrator.rollback(started_containers, previous_profile, stopped_services)
    telemetry.emit("switch.error", {"reason": str(e)})
    raise
```

---

## OTLP Tracing

The entire `switch_environment()` function is wrapped with `@otlp_span("switch.pipeline")`:

```python
@otlp_span("switch.pipeline")
def switch_environment(name: str) -> None:
    ...
```

This creates a root span for the entire switch operation. Each sub-step (service start, container run, hook execute) creates child spans, giving full visibility in tools like Jaeger or Grafana Tempo.

---

## Service Orchestration

Services are started/stopped via `systemctl`:

```
required_services: [steam, pipewire]
optional_services: [bottles, discord]
```

- **Required**: `systemctl start <service>` — failure raises `SwitchError` and triggers rollback
- **Optional**: `systemctl start <service>` — failure logs `WARNING` and continues

Dry-run mode (activated when `systemctl` is not found or `GATEOS_DRY_RUN=1`) logs all operations without executing them.

---

## Container Orchestration

Containers are started via `podman run` (or `docker run` as fallback):

```yaml
containers:
  - name: redis
    image: redis:7
    ports: ["6379:6379"]
    env: {REDIS_PASSWORD: ""}
    volumes: ["/tmp/data:/data"]
```

Gate-OS tracks started containers in a list. On rollback, `podman stop` is called for each.

---

## Plugin Hooks

Plugins registered via entry-points receive `pre_switch` and `post_switch` calls:

```python
registry.invoke("pre_switch", environment=manifest)
# ... switch pipeline ...
registry.invoke("post_switch", environment=manifest)
```

Plugin errors are caught, logged, and **do not abort the switch** (unlike required service failures).

---

## Error Handling

| Failure Type | Behavior |
|---|---|
| Invalid manifest (schema) | Abort before any changes; raise `ValidationError` |
| Required service start fails | Rollback + raise `SwitchError` |
| Optional service start fails | Log warning; continue |
| Container start fails | Rollback + raise `SwitchError` |
| Plugin hook raises exception | Log error; continue |
| Hardware profile apply fails | Rollback + raise `SwitchError` |

---

## Source

- `gateos_manager/orchestrator.py` — `switch_environment()`, `rollback()`
- `gateos_manager/services/manager.py` — service start/stop
- `gateos_manager/containers/manager.py` — container start/stop
- `gateos_manager/profiles/hardware.py` — hardware profile apply
- `gateos_manager/security/policy.py` — security policy apply
- `gateos_manager/plugins/registry.py` — plugin hook invocation

---

## See Also
- [Architecture Overview](overview.md)
- [Environments & Manifests](environments.md)
- [OTLP Observability](../observability/otlp.md)
- [Sequence Diagrams](../diagrams/env-switch-sequence.md)
