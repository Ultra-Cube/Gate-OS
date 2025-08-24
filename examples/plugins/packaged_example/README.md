# Packaged Example Plugin

Demonstrates structure for distributing a Gate-OS plugin as an installable Python package.

## Layout

```text
packaged_example/
  pyproject.toml
  src/
    gateos_plugin_example/
      __init__.py
      hooks.py
```

## hooks.py

```python
from gateos_manager.plugins.registry import register

@register('post_switch')
def announce(ctx):
    ctx['telemetry'].emit('plugin_example', {'containers': ctx.get('started_containers', [])})
```

## Install (development)

```bash
pip install -e ./packaged_example
```
