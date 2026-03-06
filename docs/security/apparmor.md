# AppArmor & Security Policy

Gate-OS enforces per-environment security policies through a **capability allowlist** and integration stubs for AppArmor profiles.

---

## Security Policy Manifest Fields

```yaml
security_policy:
  isolation_level: balanced     # strict | balanced | permissive
  capability_allowlist:
    - NET_BIND_SERVICE
    - SYS_NICE
    - CHOWN
```

### Isolation Levels

| Level | Description |
|---|---|
| `strict` | Minimal capability set; blocks most privileged operations |
| `balanced` | Default — allows common capabilities needed for desktop apps |
| `permissive` | Nearly unrestricted; for legacy/compatibility environments only |

---

## Capability Allowlist

The capability allowlist is defined in `capability-policy.json` and enforced via `gateos_manager/security/policy.py`:

```python
def enforce_capabilities(manifest: dict) -> None:
    policy = load_capability_policy()
    requested = manifest.get("security_policy", {}).get("capability_allowlist", [])
    for cap in requested:
        if cap not in policy["allowed_capabilities"]:
            raise PolicyViolationError(f"Capability not allowed: {cap}")
```

Attempting to use a capability not in the allowlist raises a `PolicyViolationError` and aborts the switch.

---

## AppArmor Integration

AppArmor profile stubs are applied via `apply_isolation()` in `gateos_manager/security/isolation.py`:

```python
def apply_isolation(environment: str, level: str) -> None:
    profile_path = f"/etc/apparmor.d/gateos.{environment}"
    if os.path.exists(profile_path):
        subprocess.run(["apparmor_parser", "-r", profile_path], check=True)
    else:
        logger.warning(f"No AppArmor profile found for {environment}; skipping")
```

### Profile Locations
- `/etc/apparmor.d/gateos.gaming` — gaming environment profile
- `/etc/apparmor.d/gateos.dev` — development environment profile
- `/etc/apparmor.d/gateos.design` — design environment profile

### Generating Profiles (Manual, v1.x)
AppArmor profile generation from manifest is planned for v1.3.0. For now, create profiles manually:

```bash
sudo tee /etc/apparmor.d/gateos.gaming << 'EOF'
#include <tunables/global>
profile gateos.gaming flags=(attach_disconnected) {
  #include <abstractions/base>
  network inet stream,
  capability net_bind_service,
  capability sys_nice,
  /tmp/** rw,
}
EOF
sudo apparmor_parser -r /etc/apparmor.d/gateos.gaming
```

---

## seccomp Filtering

seccomp integration is planned for v1.3.0. The `apply_isolation()` stub currently logs the intended seccomp profile name but does not apply it:

```python
# TODO(v1.3.0): apply seccomp profile
logger.info(f"seccomp profile: gateos-{level}.json (not yet applied)")
```

---

## Container Security

For containers defined in manifests, Gate-OS plans to pass `--cap-drop ALL --cap-add <allowlist>` to container runtime calls in v1.3.0.

Current state: containers are started without explicit capability restrictions.

---

## See Also
- [Security Overview](overview.md)
- [Manifest Signing](signing.md)
- [Threat Model](threat-model.md)
