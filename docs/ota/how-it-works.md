# OTA Updates — How It Works

Gate-OS supports **over-the-air (OTA) updates** that check the GitHub Releases API for new versions and download them without requiring manual package management.

---

## Architecture

```
gateos check-update
       │
       ▼
  [1] GitHub Releases API
      GET /repos/Ultra-Cube/Gate-OS/releases/latest
       │
       ▼
  [2] Version Comparison
      current_version < latest_version (semver)
       │              │
    No update      Update available
       │              │
      Exit 0          ▼
              Print version + download URL

gateos apply-update [--yes]
       │
       ▼
  [3] HEAD request to download URL (dry-run)
       │              │
  --yes not set    --yes set
       │              │
   Print URL         Download .deb / .tar.gz
   Exit 0              │
                       ▼
                   Write to GATEOS_UPDATE_DIR
                   Write .ready marker file
```

---

## CLI Commands

### Check for Updates

```bash
gateos check-update
```

Output (update available):
```
Latest version: v1.3.0
Download URL: https://github.com/Ultra-Cube/Gate-OS/releases/download/v1.3.0/gate-os_1.3.0_amd64.deb
Run `gateos apply-update --yes` to download.
```

Output (up to date):
```
Gate-OS v1.2.0 is up to date.
```

Include pre-releases:
```bash
gateos check-update --include-prerelease
```

### Apply Updates

```bash
# Dry-run (default) — HEAD request to validate URL, print info
gateos apply-update

# Download and stage
gateos apply-update --yes
```

---

## Implementation Details

`gateos_manager/updater.py`:

```python
def check_for_update(include_prerelease: bool = False) -> dict | None:
    """Returns release info dict if a newer version exists, else None."""
    url = f"{GATEOS_UPDATE_BASE_URL}/latest"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    release = resp.json()
    latest = release["tag_name"].lstrip("v")
    current = get_current_version()
    if semver_gt(latest, current):
        return {"version": latest, "assets": release["assets"]}
    return None

def apply_update(download_url: str, yes: bool = False) -> Path:
    """Downloads the update package into GATEOS_UPDATE_DIR."""
    update_dir = Path(os.environ.get("GATEOS_UPDATE_DIR", "/tmp/gateos-updates"))
    update_dir.mkdir(parents=True, exist_ok=True)
    filename = update_dir / Path(download_url).name
    if yes:
        resp = requests.get(download_url, stream=True, timeout=30)
        resp.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        (update_dir / ".ready").write_text(str(filename))
    return filename
```

---

## Update Directory Layout

```
$GATEOS_UPDATE_DIR/    (default: /tmp/gateos-updates/)
  gate-os_1.3.0_amd64.deb   — downloaded package
  .ready                      — marker file containing package path
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `GATEOS_UPDATE_BASE_URL` | GitHub Releases API URL | Override for private mirror |
| `GATEOS_UPDATE_DIR` | `/tmp/gateos-updates` | Download staging directory |
| `GATEOS_CURRENT_VERSION` | From package metadata | Override for testing |

---

## See Also
- [Schedule & Apply](schedule-apply.md) — automatic update scheduling
- [Configuration](../getting-started/configuration.md) — update-related env vars
- [Supply Chain](../architecture/supply-chain.md) — update artifact signing
