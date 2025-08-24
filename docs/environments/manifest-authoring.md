# Environment Manifest Authoring Guide

## Purpose
Define reproducible environment roles (dev, design, media, etc.) via declarative YAML/JSON.

## Minimal Example
```yaml
environment:
  name: dev
  version: 0.1.0
  description: Developer toolchain
containers:
  - name: toolchain
    image: ghcr.io/org/dev-toolchain:latest
```

## Top-Level Sections (Current)
| Section | Required | Description |
|---------|----------|-------------|
| environment | Yes | Metadata: name, description, category, version |
| containers | No | List of container definitions (name, image, mounts, env) |
| profiles | No | Resource & security tuning knobs |
| workflows | No | Declarative future-trigger actions |

## Container Fields (Subset)
| Field | Required | Notes |
|-------|----------|-------|
| name | Yes | Unique within manifest |
| image | Yes | Use digest for supply chain integrity (future enforcement) |
| gpu | No | Flag for runtime GPU handling (planned) |
| mounts | No | host/target path pairs |
| env | No | Per-container environment variables |

## Profiles (Draft Schema)
```yaml
profiles:
  resource:
    cpu_shares: high   # low|normal|high
    io_priority: high  # low|normal|high
  security:
    capability_allowlist:
      - NET_BIND_SERVICE
    isolation: relaxed # strict|relaxed (future semantics)
```

## Validation
Use CLI validator:
```bash
gateos validate path/to/manifest.yaml --schema docs/architecture/schemas/environment-manifest.schema.yaml
```

## Best Practices
- Prefer explicit versions or digests for images
- Keep description succinct (<120 chars)
- Minimize capability allowlist entries
- Group related mounts under dedicated host directories
- Use `workflows` for automation rather than embedding logic in plugins

## Roadmap Additions
| Feature | Status |
|---------|--------|
| Signing (cosign) | Planned |
| Policy annotations | Planned |
| Variable substitution | Under consideration |
| Conditional blocks | Exploration |
