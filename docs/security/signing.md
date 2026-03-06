# Manifest Signing

Gate-OS uses **Ed25519** asymmetric signing to guarantee manifest integrity and authenticity. A signed manifest cannot be tampered with without invalidating the signature.

---

## Implementation

Signing is implemented in `gateos_manager/security/signing.py` using PyNaCl:

- `generate_keypair(key_dir)` — generates `signing.key` (private) and `signing.pub` (public)
- `sign(manifest_path, key_dir)` — signs the manifest file; writes `<manifest>.sig`
- `verify(manifest_path, key_dir)` — verifies the signature file against the manifest content

Algorithm: **Ed25519** (Curve25519 / NaCl)  
Signature file: `<manifest_name>.yaml.sig` (base64-encoded)

---

## Setup

### 1. Generate a Keypair

```bash
gateos gen-keypair --key-dir /etc/gateos/keys
```

This creates:
- `/etc/gateos/keys/signing.key` — private key (keep secret, chmod 600)
- `/etc/gateos/keys/signing.pub` — public key (distribute with deployment)

```bash
chmod 600 /etc/gateos/keys/signing.key
chmod 644 /etc/gateos/keys/signing.pub
```

!!! warning "Private Key Protection"
    The private key (`signing.key`) must **never** be committed to version control or distributed. Keep it only on the signing machine or in a secret manager.

---

### 2. Sign a Manifest

```bash
gateos sign environments/gaming.yaml --key-dir /etc/gateos/keys
```

Output:
```
Signed: environments/gaming.yaml  ->  environments/gaming.yaml.sig
```

The `.sig` file is a base64-encoded Ed25519 signature of the manifest's SHA-256 hash.

---

### 3. Verify a Signature

```bash
gateos verify environments/gaming.yaml --key-dir /etc/gateos/keys
```

Output:
```
OK: signature valid for environments/gaming.yaml
```

If the manifest was modified after signing:
```
FAIL: signature invalid for environments/gaming.yaml
```

---

## CI/CD Integration

Sign manifests as part of a release pipeline:

```yaml
# .github/workflows/release.yml
- name: Sign manifests
  run: |
    gateos sign environments/gaming.yaml --key-dir ${{ secrets.KEY_DIR }}
    gateos sign environments/dev.yaml --key-dir ${{ secrets.KEY_DIR }}
  env:
    NACL_SIGNING_KEY: ${{ secrets.NACL_SIGNING_KEY }}
```

---

## Verification in Switch Pipeline

In v1.3.0, the switch engine will automatically verify manifest signatures before executing:

```python
# Planned v1.3.0 behaviour
if os.environ.get("GATEOS_REQUIRE_SIGNED_MANIFESTS"):
    verify(manifest_path, key_dir=os.environ["GATEOS_KEY_DIR"])
```

Until then, verification is manual via `gateos verify`.

---

## Security Properties

| Property | Value |
|---|---|
| Algorithm | Ed25519 (NaCl / PyNaCl) |
| Key size | 256-bit private key, 256-bit public key |
| Signature size | 64 bytes (base64: 88 chars) |
| Collision resistance | SHA-256 pre-image |
| Forward secrecy | Not applicable (asymmetric signing) |

---

## See Also
- [Security Overview](overview.md)
- [AppArmor & Policies](apparmor.md)
- [Supply Chain Integrity](../architecture/supply-chain.md)
