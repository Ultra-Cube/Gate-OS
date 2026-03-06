# Environments & Manifests

Gate-OS environments are defined by **YAML manifest files**. Each manifest is a self-contained specification of the services, containers, hardware profile, and security policy that should be active when the environment is running.

---

## Manifest Structure

```yaml
name: gaming                    # Unique environment name (required)
description: Optimised for gaming and streaming
category: gaming                # gaming | development | design | media

services:
  required:
    - steam                     # systemd services that MUST start (abort on failure)
    - pipewire
  optional:
    - bottles                   # systemd services — failure logs warning but continues

containers:
  - name: soundboard
    image: redis:7              # Container image
    ports:
      - "6379:6379"
    env:
      REDIS_PASSWORD: ""
    volumes:
      - "/tmp/soundboard:/data"

hardware_profile:
  cpu_governor: performance     # performance | powersave | ondemand
  gpu_power_mode: high          # high | auto | low (NVIDIA/AMD)
  nic_priority: gaming          # gaming | default | background

security_policy:
  isolation_level: balanced     # strict | balanced | permissive
  capability_allowlist:
    - NET_BIND_SERVICE
    - SYS_NICE

hooks:
  pre_switch:
    - type: shell
      command: "notify-send 'Switching to Gaming'"
  post_switch:
    - type: shell
      command: "pkill -9 code || true"
```

---

## Environment Types

### Gaming
Optimises for low-latency, maximum GPU utilisation, and streaming.
- CPU: `performance` governor
- GPU: `high` power mode
- Services: `steam`, `pipewire`, `gamemode`
- Example: `environments/gaming.yaml`

### Development
Optimises for memory bandwidth and battery life during coding sessions.
- CPU: `ondemand` governor
- Services: `docker`, `redis`, `postgresql`
- Containers: Dev databases, language servers
- Example: `environments/dev.yaml`

### Design
Optimises for GPU compute (GPU acceleration for Blender, DaVinci Resolve).
- CPU: `performance` governor
- GPU: `high` power mode
- Services: `pipewire` (audio), `wacom` (drawing tablet driver)
- Example: `environments/design.yaml`

### Media
Optimises for audio fidelity and display color accuracy.
- CPU: `powersave` governor
- Services: `pipewire-pulse`, `mpd`, `jellyfin`
- Example: `environments/media.yaml`

---

## Manifest Validation

Gate-OS validates every manifest against a JSON Schema before executing any switch:

```bash
gateos validate environments/gaming.yaml
# OK: environments/gaming.yaml

gateos validate environments/bad.yaml
# FAIL: environments/bad.yaml: 'name' is a required property
```

The schema is at `gateos_manager/manifest/schemas/environment-manifest-v1.0.yaml`.

### Required Fields
- `name` (string, unique)
- `description` (string)
- `category` (enum: `gaming | development | design | media | custom`)

### Optional Sections
- `services` (with `required` and `optional` sub-lists)
- `containers` (list of container specs)
- `hardware_profile` (CPU, GPU, NIC settings)
- `security_policy` (isolation level + capability allowlist)
- `hooks` (pre/post switch shell commands)

---

## Manifest Directory

By default, Gate-OS scans the `environments/` directory relative to the working directory. Override with:

```bash
export GATEOS_MANIFEST_DIR=/etc/gateos/environments
```

---

## Manifest Signing

Sign manifests before distributing to ensure integrity:

```bash
gateos gen-keypair --key-dir /etc/gateos/keys
gateos sign environments/gaming.yaml --key-dir /etc/gateos/keys
gateos verify environments/gaming.yaml --key-dir /etc/gateos/keys
```

See [Signing Guide](../security/signing.md) for details.

---

## See Also
- [Switch Engine](switch-engine.md) — how the switch pipeline works
- [Security Overview](../security/overview.md) — signing and isolation
- [Configuration](../getting-started/configuration.md) — manifest directory env vars
