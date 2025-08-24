# Examples

Practical sample assets to explore Gate-OS concepts.

## Environments (`examples/environments/`)

| File | Purpose |
|------|---------|
| `dev.yaml` | Draft developer environment manifest |
| `gaming.yaml` | Draft gaming environment manifest |
| `security.yaml` | Draft security toolkit manifest (capability allowlist enforced) |

Validate manifests:

```bash
gateos validate examples/environments/*.yaml --schema docs/architecture/schemas/environment-manifest.schema.yaml
```

## Plugins (`examples/plugins/`)

| File | Hook(s) | Notes |
|------|---------|-------|
| `sample_plugin.py` | `pre_switch` | Prints message before switching |

Register custom plugin:

```python
from gateos_manager.plugins import registry

def my_hook(environment, manifest):
    ...
registry.register('pre_switch', my_hook)
```

## Container Dry-Run

Set dry-run to simulate container startup:

```bash
export GATEOS_CONTAINER_DRY_RUN=1
python -c "from gateos_manager.containers.manager import ContainerManager;print(ContainerManager().start({'name':'demo','containers':[{'name':'redis','image':'redis:7'}]}))"
```
