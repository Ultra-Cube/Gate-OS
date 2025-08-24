from gateos_manager.plugins.registry import register

@register('post_switch')
def announce(ctx):
    ctx['telemetry'].emit('plugin_example', {'containers': ctx.get('started_containers', [])})
