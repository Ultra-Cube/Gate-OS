"""Sample plugin for Gate-OS plugin registry."""
from gateos_manager.plugins import registry

def announce_pre_switch(environment, manifest):
    print(f"[PLUGIN] About to switch to: {environment}")

registry.register('pre_switch', announce_pre_switch)
