import threading
import queue
from pathlib import Path


def test_cancel_process_logs_and_event(tmp_path, monkeypatch):
    # monkeypatch logger paths to tmp
    import logger_json
    monkeypatch.setattr(logger_json, 'LOG_DIR', tmp_path)
    monkeypatch.setattr(logger_json, 'LOG_FILE', tmp_path / 'import.log')
    tmp_path.mkdir(exist_ok=True)

    # create a minimal dummy self with required attributes
    from ui import app as ui_app_module

    Dummy = type('D', (), {})
    d = Dummy()
    d.cancel_event = threading.Event()
    d.event_q = queue.Queue()

    # signal cancel before processing
    d.cancel_event.set()

    sample = str(Path('documents/test_samples/sample.pdf').resolve())

    # call the bound method _process_path directly with dummy self
    ui_app_module.App._process_path(d, sample)

    # check event queued
    evt = d.event_q.get_nowait()
    assert evt[0] == sample
    assert evt[1] == 'Cancelado'

    # check log file has cancelled entry
    content = (tmp_path / 'import.log').read_text(encoding='utf-8')
    assert 'cancelled' in content
