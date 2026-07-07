from pathlib import Path
import asyncio
from importer import import_folder


def test_importer_writes_log(tmp_path, monkeypatch):
    # use a temporary logs directory by monkeypatching LOG_DIR in logger_json
    import logger_json

    monkeypatch.setattr(logger_json, 'LOG_DIR', tmp_path)
    monkeypatch.setattr(logger_json, 'LOG_FILE', tmp_path / 'import.log')

    res = asyncio.run(import_folder('documents/test_samples', recursive=False, patterns=['*.pdf'], skip_if_pdfa=False))
    # after running, check that log file exists and has at least one line
    log_file = tmp_path / 'import.log'
    assert log_file.exists()
    content = log_file.read_text(encoding='utf-8').strip()
    assert content != ''
