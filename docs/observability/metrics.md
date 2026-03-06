# Prometheus Metrics

Gate-OS exposes Prometheus-compatible metrics for monitoring environment switches, API requests, and system state.

---

## Implementation

Metrics are defined in `gateos_manager/telemetry/prometheus.py` using a custom lightweight registry (no `prometheus_client` dependency required):

```python
class Counter:
    def increment(self, labels: dict = None) -> None: ...

class Gauge:
    def set(self, value: float, labels: dict = None) -> None: ...

class Histogram:
    def observe(self, value: float, labels: dict = None) -> None: ...
```

---

## Available Metrics

### Counters

| Metric | Labels | Description |
|---|---|---|
| `gateos_switch_total` | `environment`, `status` | Total environment switch attempts (status: `success`, `failure`) |
| `gateos_api_requests_total` | `method`, `path`, `status_code` | Total HTTP requests to the Control API |
| `gateos_ota_check_total` | `result` | OTA update check results (result: `update_available`, `up_to_date`, `error`) |
| `gateos_plugin_invocations_total` | `hook`, `plugin`, `status` | Plugin hook invocations |

### Gauges

| Metric | Labels | Description |
|---|---|---|
| `gateos_active_environment` | `name` | Currently active environment (1 = active, 0 = inactive) |
| `gateos_containers_running` | `environment` | Number of containers currently running per environment |
| `gateos_services_running` | `environment` | Number of systemd services currently running per environment |

### Histograms

| Metric | Labels | Buckets | Description |
|---|---|---|---|
| `gateos_switch_duration_seconds` | `environment` | 0.1, 0.5, 1, 2, 3, 5, 10 | End-to-end switch duration in seconds |
| `gateos_api_request_duration_seconds` | `method`, `path` | 0.01, 0.05, 0.1, 0.5, 1.0 | API request latency |

---

## Prometheus Scrape Endpoint

The Control API exposes metrics at `GET /metrics` in Prometheus text format:

```bash
curl http://localhost:8000/metrics
```

Example output:
```
# HELP gateos_switch_total Total environment switch attempts
# TYPE gateos_switch_total counter
gateos_switch_total{environment="gaming",status="success"} 12
gateos_switch_total{environment="dev",status="success"} 7
gateos_switch_total{environment="gaming",status="failure"} 1

# HELP gateos_switch_duration_seconds End-to-end switch duration
# TYPE gateos_switch_duration_seconds histogram
gateos_switch_duration_seconds_bucket{environment="gaming",le="1"} 8
gateos_switch_duration_seconds_bucket{environment="gaming",le="3"} 12
gateos_switch_duration_seconds_sum{environment="gaming"} 18.4
gateos_switch_duration_seconds_count{environment="gaming"} 12
```

---

## Grafana Dashboard

A sample Grafana dashboard JSON is available at `monitoring/grafana-dashboard.json` (planned). Key panels:

- **Switch success rate** — `rate(gateos_switch_total{status="success"}[5m])`
- **P95 switch latency** — `histogram_quantile(0.95, rate(gateos_switch_duration_seconds_bucket[5m]))`
- **Active environment** — `gateos_active_environment`
- **API error rate** — `rate(gateos_api_requests_total{status_code=~"5.."}[5m])`

---

## Prometheus Scrape Config

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'gate-os'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
    scrape_interval: 15s
```

---

## See Also
- [OTLP Tracing](otlp.md)
- [Switch Engine](../architecture/switch-engine.md)
- [API Reference](../api/control-api.md)
