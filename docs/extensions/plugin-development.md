# Plugin Development Guide

## Overview
Plugins extend switch lifecycle via hooks: `pre_switch`, `post_switch`, `shutdown`.

## Registration
Entry point style (future) or manual dynamic import. For now place plugin Python file in a discoverable path and register via a registry call.

## Hook Contracts (Current)
| Hook | Args | Expected Behavior | Error Handling |
|------|------|------------------|----------------|
| pre_switch | context(dict) | Validate / mutate safe fields; raise to abort | Raise exception aborts switch |
| post_switch | context(dict) | Emit metrics, UI refresh triggers | Exceptions logged, not fatal |
| shutdown | context(dict) | Cleanup resources on failure | Exceptions logged |

## Context Fields (Partial, evolving)
| Field | Description |
|-------|-------------|
| manifest | Parsed environment manifest dict |
| started_containers | List of container names activated |
| telemetry | Emitter instance (emit(event_type, payload)) |

## Minimal Example
```python
from gateos_manager.plugins.registry import register

@register('pre_switch')
def check_manifest(ctx):
    manifest = ctx['manifest']
    if manifest.get('environment', {}).get('name') == 'forbidden':
        raise ValueError('environment name forbidden')

@register('post_switch')
def announce(ctx):
    ctx['telemetry'].emit('switch_complete', {'count': len(ctx.get('started_containers', []))})
```

## Testing Plugins
Use pytest and create a fake context dict. Ensure errors propagate or are logged depending on hook.

## Roadmap
- Distribution via entrypoints
- Sandboxed execution layer
- Versioned plugin API surface
