import json
import os

from gateos_manager.logging import structured
from gateos_manager.plugins import registry


def test_plugin_registry_register_and_invoke(capsys):
    calls = []
    def hook(environment, manifest):
        calls.append(environment)
    registry.register('pre_switch', hook)
    registry.invoke('pre_switch', environment='envx', manifest={})
    assert calls == ['envx']
    summary = registry.list_hooks()
    assert 'pre_switch' in summary and summary['pre_switch'] >= 1


def test_structured_logging_output(capsys):
    os.environ['GATEOS_LOG_LEVEL'] = 'DEBUG'
    structured.debug('debug-msg', correlation_id='cid123', extra='val')
    structured.info('info-msg', correlation_id='cid456')
    captured = capsys.readouterr().out.strip().splitlines()
    # Should have at least one line
    assert any('debug-msg' in line for line in captured)
    line_obj = json.loads(captured[-1])
    assert 'correlation_id' in line_obj
