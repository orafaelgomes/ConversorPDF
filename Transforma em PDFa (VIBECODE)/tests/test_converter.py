import subprocess
import platform


def test_run_subprocess_windows_creationflags(monkeypatch):
    # Simula Windows e intercepta subprocess.Popen
    calls = {}

    class DummyProc:
        def __init__(self, *args, **kwargs):
            calls['args'] = args
            calls['kwargs'] = kwargs
            self.returncode = 0

        def communicate(self, timeout=None):
            return (b'ok', b'')

    monkeypatch.setattr(platform, 'system', lambda: 'Windows')
    monkeypatch.setattr(subprocess, 'Popen', DummyProc)

    from converter import convert_with_ghostscript

    res = convert_with_ghostscript('in.pdf', 'out.pdf')
    assert res['returncode'] == 0
    assert 'creationflags' in calls['kwargs']


def test_run_subprocess_unix_no_creationflags(monkeypatch):
    calls = {}

    class DummyProc:
        def __init__(self, *args, **kwargs):
            calls['args'] = args
            calls['kwargs'] = kwargs
            self.returncode = 0

        def communicate(self, timeout=None):
            return (b'ok', b'')

    monkeypatch.setattr(platform, 'system', lambda: 'Linux')
    monkeypatch.setattr(subprocess, 'Popen', DummyProc)

    from converter import convert_with_ghostscript

    res = convert_with_ghostscript('in.pdf', 'out.pdf')
    assert res['returncode'] == 0
    assert 'creationflags' not in calls['kwargs']
