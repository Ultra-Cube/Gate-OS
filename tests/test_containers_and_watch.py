import os

from gateos_manager.containers.manager import ContainerManager
from gateos_manager.watch.reloader import _Handler  # type: ignore


def test_container_manager_dry_run_start_stop():
    os.environ['GATEOS_CONTAINER_DRY_RUN'] = '1'
    manifest = {
        'name': 'dev',
        'containers': [
            {'name': 'redis', 'image': 'redis:7', 'ports': ['6379:6379'], 'env': {'FOO': 'BAR'}},
            {'name': 'api', 'image': 'busybox', 'command': 'sleep 1'}
        ]
    }
    mgr = ContainerManager()
    started = mgr.start(manifest, correlation_id='test')
    assert len(started) == 2
    status = mgr.status(manifest)
    assert all(v == 'running' for v in status.values())
    stopped = mgr.stop(manifest, correlation_id='test')
    assert len(stopped) == 2
    status = mgr.status(manifest)
    assert all(v == 'stopped' for v in status.values())


def test_isolation_stub_enabled(monkeypatch):
    os.environ['GATEOS_CONTAINER_DRY_RUN'] = '1'
    os.environ['GATEOS_SECURITY_ENFORCE'] = '1'
    manifest = {'name': 'secure', 'containers': [{'name': 'app', 'image': 'alpine'}]}
    mgr = ContainerManager()
    mgr.start(manifest, correlation_id='sec')
    # isolation stub does not change state; just ensure running
    status = mgr.status(manifest)
    assert list(status.values()) == ['running']


def test_watch_handler_triggers_callback(tmp_path):
    triggered = []
    def cb():
        triggered.append(1)
    handler = _Handler(cb)
    # simulate yaml file modified event
    class E:
        is_directory = False
        src_path = str(tmp_path / 'env.yaml')
    handler.on_any_event(E())
    assert triggered == [1]
