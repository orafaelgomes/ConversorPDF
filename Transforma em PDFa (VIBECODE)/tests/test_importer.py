import asyncio
from pathlib import Path
from importer import scan_folder, build_queue, import_folder


def test_scan_folder_single_file():
    p = Path("documents/test_samples/sample.pdf")
    files = list(scan_folder(str(p), recursive=False))
    assert len(files) == 1


def test_build_queue():
    p = Path("documents/test_samples/sample.pdf")
    q = build_queue([p])
    assert isinstance(q, list)
    assert q[0]["path"].endswith("sample.pdf")


def test_import_folder_no_skip():
    res = asyncio.run(import_folder("documents/test_samples", recursive=False, patterns=["*.pdf"], skip_if_pdfa=False))
    assert isinstance(res, list)
