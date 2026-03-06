# Plugin Development Guide

Gate-OS provides a **plugin API** that lets you extend environment switching behaviour by registering hooks that run before and after a switch.

---

## Plugin API

Plugins are Python packages that register **entry points** under the `gateos.plugins` group. Gate-OS discovers them automatically at runtime via `importlib.metadata`.

### Hook Points

| Hook | When | Use Cases |
|---|---|---|
| `pre_switch` | Before services stop; before any changes | Notify user; save application state; check preconditions |
| `post_switch` | After containers start; after all changes | Open apps; configure desktop; send webhook notification |
| `shutdown` | When Gate-OS API shuts down | Cleanup; persist state |

---

## Creating a Plugin

### 1. Create the package structure

```
my-gateos-plugin/
├── pyproject.toml
└── my_gateos_plugin/
    └── __init__.py
```

### 2. Implement the hook functions

```python
# my_gateos_plugin/__init__.py

def pre_switch(environment: dict, **kwargs) -> None:
    """Called before the switch starts."""
    env_name = environment.get("name", "unknown")
    print(f"[my-plugin] Preparing to switch to: {env_name}")

def post_switch(environment: dict, **kwargs) -> None:
    """Called after the switch completes successfully."""
    env_name = environment.get("name", "unknown")
    print(f"[my-plugin] Switch complete: {env_name}")

def shutdown(**kwargs) -> None:
    """Called when Gate-OS shuts down."""
    print("[my-plugin] Cleanup on shutdown")
```

**Important notes:**
- Return value is ignored
- Exceptions are caught, logged, and **do not abort the switch** — plugins are advisory
- Use `**kwargs` to stay forward-compatible with future arguments

### 3. Register entry points

```toml
# pyproject.toml
[project.entry-points."gateos.plugins"]
my_plugin = "my_gateos_plugin"
```

Or for setuptools:
```python
# setup.py
entry_points={
    "gateos.plugins": [
        "my_plugin = my_gateos_plugin",
    ],
}
```

### 4. Install the plugin

```bash
pip install ./my-gateos-plugin
# or
pip install my-gateos-plugin    # from PyPI
```

Gate-OS will discover it automatically on the next start.

---

## Plugin Discovery

Gate-OS discovers plugins via `gateos_manager/plugins/registry.py`:

```python
def discover_entrypoint_plugins() -> list:
    """Returns all entry-point plugins registered under 'gateos.plugins'."""
    plugins = []
    for ep in importlib.metadata.entry_points(group="gateos.plugins"):
        module = ep.load()
        plugins.append(module)
    return plugins
```

Plugins are discovered once at startup. Restart Gate-OS after installing a new plugin.

---

## Plugin Invocation

```python
def invoke(hook: str, **kwargs) -> None:
    """Invoke all plugins for the given hook point."""
    for plugin in self.plugins:
        fn = getattr(plugin, hook, None)
        if fn and callable(fn):
            try:
                fn(**kwargs)
            except Exception as e:
                logger.error(f"Plugin {plugin.__name__}.{hook} raised: {e}")
```

- All discovered plugins implementing `hook` are called sequentially
- Errors are logged but **do not interrupt** the switch pipeline

---

## Example: Desktop Notification Plugin

```python
# notify_plugin/__init__.py
import subprocess

def pre_switch(environment: dict, **kwargs) -> None:
    name = environment.get("name", "?")
    subprocess.run(["notify-send", f"Gate-OS: switching to {name}"], check=False)

def post_switch(environment: dict, **kwargs) -> None:
    name = environment.get("name", "?")
    subprocess.run(["notify-send", f"Gate-OS: {name} ready"], check=False)
```

```toml
# pyproject.toml
[project.entry-points."gateos.plugins"]
notify = "notify_plugin"
```

---

## Example: Webhook Plugin

```python
# webhook_plugin/__init__.py
import os, requests

WEBHOOK_URL = os.environ.get("GATEOS_WEBHOOK_URL", "")

def post_switch(environment: dict, **kwargs) -> None:
    if WEBHOOK_URL:
        requests.post(WEBHOOK_URL, json={"event": "switch", "env": environment.get("name")}, timeout=5)
```

---

## Listing Installed Plugins

```bash
gateos plugins list
```

Output:
```
Installed Gate-OS plugins:
  notify_plugin  (notify-gateos-plugin 1.0.0)
  webhook_plugin (webhook-gateos-plugin 0.3.1)
```

---

## Security Considerations

!!! warning "Plugin Trust"
    Plugins run **in-process** with the same privileges as Gate-OS. Only install plugins from trusted sources. Plugin sandboxing via subprocess isolation is planned for v1.3.0.

- Verify plugin authorship before installing
- Prefer plugins that are open source and have CI/CD
- Check for entry-point hijacking in transitive dependencies

---

## See Also
- [Security Overview](../security/overview.md) — plugin security model
- [Architecture Overview](../architecture/overview.md) — where plugins fit in the system
- [Contributing](../contributing.md) — how to contribute a plugin to the main repo
