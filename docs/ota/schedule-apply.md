# OTA — Schedule & Apply

Gate-OS supports **automatic update scheduling** via two strategies: systemd drop-in timer (Strategy 1) and flag-file polling (Strategy 2).

---

## Strategy 1 — systemd Drop-in Timer (Recommended)

Creates a systemd timer that runs `gateos apply-update --yes` on a schedule.

```bash
gateos schedule-apply --strategy systemd --interval daily
```

This creates:
- `/etc/systemd/system/gateos-update.service` — the update service unit
- `/etc/systemd/system/gateos-update.timer` — the timer (daily by default)

```ini
# gateos-update.service
[Unit]
Description=Gate-OS OTA Update
After=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/bin/gateos apply-update --yes
Environment=GATEOS_UPDATE_DIR=/var/lib/gateos/updates

[Install]
WantedBy=multi-user.target
```

```ini
# gateos-update.timer
[Unit]
Description=Run Gate-OS OTA Update daily

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

After creation:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gateos-update.timer
```

---

## Strategy 2 — Flag-file Polling (Fallback)

When `systemctl` is not available (WSL, Docker containers, non-systemd init), Gate-OS uses a flag file to signal that an update is ready to apply.

```bash
gateos schedule-apply --strategy flag-file --poll-interval 3600
```

This spawns a background thread that:
1. Every `--poll-interval` seconds (default: 3600 = 1 hour)
2. Calls `check_for_update()`
3. If an update is available, writes `$GATEOS_UPDATE_DIR/.ready` with the download URL
4. On the next `gateos switch` after `.ready` exists, prints a warning:
   ```
   WARNING: Update available (v1.3.0). Run `gateos apply-update --yes` to install.
   ```

---

## Implementation

`gateos_manager/updater.py`:

```python
def schedule_apply(strategy: str = "systemd", interval: str = "daily") -> None:
    if strategy == "systemd":
        _write_systemd_units(interval)
        logger.info("systemd timer units written; run: systemctl enable --now gateos-update.timer")
    elif strategy == "flag-file":
        _start_flag_file_poller(interval_seconds=3600)
        logger.info("Flag-file poller started in background thread")
    else:
        raise ValueError(f"Unknown schedule strategy: {strategy}")
```

---

## Checking Scheduled Update Status

```bash
# systemd strategy
systemctl status gateos-update.timer
systemctl list-timers gateos-update.timer

# flag-file strategy
ls -la $GATEOS_UPDATE_DIR/
cat $GATEOS_UPDATE_DIR/.ready
```

---

## Cancelling Scheduled Updates

```bash
# systemd strategy
sudo systemctl disable --now gateos-update.timer
sudo rm /etc/systemd/system/gateos-update.{service,timer}
sudo systemctl daemon-reload

# flag-file strategy
rm -f $GATEOS_UPDATE_DIR/.ready
# Restart Gate-OS API to kill polling thread
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `GATEOS_UPDATE_DIR` | `/tmp/gateos-updates` | Where `.ready` flag file is written |
| `GATEOS_UPDATE_BASE_URL` | GitHub Releases API URL | Override for private update mirror |

---

## See Also
- [How OTA Works](how-it-works.md) — check and apply pipeline
- [Configuration](../getting-started/configuration.md) — OTA env vars
- [Supply Chain](../architecture/supply-chain.md) — update artifact signing
