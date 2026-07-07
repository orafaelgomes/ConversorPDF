"""
Módulo de conversão (Fase 4) — execução de processos de conversão em background
garantindo que nenhuma janela de console seja exibida no Windows.

Fornece `convert_with_ghostscript(input_path, output_path, timeout=None)` que
invoca o Ghostscript de forma segura e retorna um dicionário com `returncode`,
`stdout`, `stderr` e `timeout`.
"""
import subprocess
import platform
import shutil
from pathlib import Path
import logging

logger = logging.getLogger("converter")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def _default_gs_exe():
    # tenta localizar binário do Ghostscript
    for name in ("gs", "gswin64c", "gswin32c"):
        p = shutil.which(name)
        if p:
            return p
    return "gs"


def _run_subprocess(cmd, timeout=None):
    kwargs = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    if platform.system() == "Windows":
        # evita janela de console no Windows
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

    logger.debug("Executando comando: %s, kwargs=%s", cmd, kwargs)
    proc = subprocess.Popen(cmd, **kwargs)
    try:
        out, err = proc.communicate(timeout=timeout)
        return {"returncode": proc.returncode, "stdout": out, "stderr": err, "timeout": False}
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate()
        return {"returncode": proc.returncode, "stdout": out, "stderr": err, "timeout": True}


def convert_with_ghostscript(input_path: str, output_path: str, timeout: int | None = None):
    gs = _default_gs_exe()
    cmd = [
        gs,
        "-dBATCH",
        "-dNOPAUSE",
        "-sDEVICE=pdfwrite",
        "-dPDFA",
        "-dPDFACompatibilityPolicy=1",
        f"-sOutputFile={output_path}",
        input_path,
    ]
    return _run_subprocess(cmd, timeout=timeout)
