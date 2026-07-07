"""
Módulo `verificador_pdfa` - Fase 1 (Core & Back-end)

Fornece uma função assíncrona `validar_pdfa(path)` que tenta validar um PDF
usando, preferencialmente, o CLI `verapdf` se disponível, ou um fallback
heurístico baseado em `PyPDF2` quando instalado.

Retorna um dicionário com `status` e `detalhes` para integração com o UI.
"""
import asyncio
import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger("verificador_pdfa")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


async def _run_verapdf(path: str) -> Dict:
    """Executa `verapdf` via subprocess assíncrono, se disponível."""
    verapdf_path = shutil.which("verapdf")
    if not verapdf_path:
        return {"available": False}

    proc = await asyncio.create_subprocess_exec(
        verapdf_path,
        path,
        "--format",
        "text",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    text_out = (stdout or b"").decode("utf-8", errors="ignore")
    text_err = (stderr or b"").decode("utf-8", errors="ignore")
    return {"available": True, "returncode": proc.returncode, "stdout": text_out, "stderr": text_err}


async def validar_pdfa(path: str) -> Dict:
    """Valida se `path` está em conformidade com PDF/A.

    Retorna um dicionário: {"status": "conforme"|"nao_conforme"|"erro", "detalhes": [...]}.
    """
    p = Path(path)
    if not p.exists():
        logger.error("Arquivo não encontrado: %s", path)
        return {"status": "erro", "detalhes": ["arquivo nao encontrado"]}

    # Primeiro: tentar usar verapdf (se instalado no sistema)
    try:
        res = await _run_verapdf(str(p))
    except Exception as e:
        logger.exception("Falha ao executar verapdf: %s", e)
        res = {"available": False}

    if res.get("available"):
        out = (res.get("stdout") or "") + "\n" + (res.get("stderr") or "")
        txt = out.lower()
        # heurística simples de análise de saída
        if "conform" in txt or "pass" in txt or "valid" in txt:
            return {"status": "conforme", "detalhes": []}
        else:
            lines = [l.strip() for l in out.splitlines() if l.strip()]
            return {"status": "nao_conforme", "detalhes": lines[:5]}

    # Fallback: heurística leve usando PyPDF2 (se instalado)
    try:
        import PyPDF2  # type: ignore

        try:
            reader = PyPDF2.PdfReader(str(p))
            info = reader.metadata or {}
            info_text = json.dumps({k: str(v) for k, v in info.items()})
            if "pdfaid" in info_text.lower() or "pdf/a" in info_text.lower() or "pdfa" in info_text.lower():
                return {"status": "conforme", "detalhes": []}
            else:
                return {"status": "nao_conforme", "detalhes": ["heuristica: metadados nao indicam PDF/A"]}
        except Exception as e:
            logger.exception("Erro ao ler PDF com PyPDF2: %s", e)
            return {"status": "erro", "detalhes": [str(e)]}
    except Exception:
        logger.info("Nem verapdf nem PyPDF2 disponíveis; retornando nao_conforme por seguranca.")
        return {"status": "nao_conforme", "detalhes": ["ferramenta de validacao ausente (verapdf/PyPDF2)"]}


def _cli():
    import argparse

    parser = argparse.ArgumentParser(description="Validador PDF/A (módulo local)")
    parser.add_argument("--input", "-i", required=True, help="Caminho para o arquivo PDF a validar")
    args = parser.parse_args()

    result = asyncio.run(validar_pdfa(args.input))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _cli()
