"""
Módulo `importer` - Fase 2 (I/O e Importação em Lote)

Fornece funcionalidade para varrer diretórios recursivamente, aplicar filtros
por padrão e enfileirar arquivos PDF para processamento posterior.
"""
from pathlib import Path
from typing import List, Dict, Iterator
import fnmatch
import argparse
import json
from logger_json import log_event
import logging
import asyncio

logger = logging.getLogger("importer")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def scan_folder(path: str, recursive: bool = True, patterns: List[str] = None) -> Iterator[Path]:
    p = Path(path)
    if patterns is None:
        patterns = ["*.pdf"]

    if not p.exists():
        raise FileNotFoundError(path)

    if p.is_file():
        if any(fnmatch.fnmatch(p.name, pat) for pat in patterns):
            yield p
        return

    if recursive:
        for f in p.rglob("*"):
            if f.is_file() and any(fnmatch.fnmatch(f.name, pat) for pat in patterns):
                yield f
    else:
        for f in p.iterdir():
            if f.is_file() and any(fnmatch.fnmatch(f.name, pat) for pat in patterns):
                yield f


def build_queue(paths: List[Path]) -> List[Dict]:
    queue = []
    for p in paths:
        stat = p.stat()
        queue.append({
            "path": str(p),
            "size": stat.st_size,
            "mtime": stat.st_mtime,
        })
    return queue


async def import_folder(path: str, recursive: bool = True, patterns: List[str] = None, skip_if_pdfa: bool = False):
    from verificador_pdfa import validar_pdfa

    found = list(scan_folder(path, recursive=recursive, patterns=patterns))
    queue = build_queue(found)
    logger.info("Arquivos detectados: %d", len(queue))

    results = []
    for item in queue:
        # logaremos o arquivo como enfileirado (JSONL) para integração com o painel
        log_event({"event": "queued", "path": item["path"], "size": item["size"]})
        if skip_if_pdfa:
            res = await validar_pdfa(item["path"])
            if res.get("status") == "conforme":
                logger.info("Pulando %s (ja e PDF/A)", item["path"])
                continue
        results.append(item)

    return results


def _cli():
    parser = argparse.ArgumentParser(description="Importador em lote de PDFs")
    parser.add_argument("--path", "-p", required=True, help="Caminho para arquivo ou diretório")
    parser.add_argument("--recursivo", action="store_true", help="Habilitar varredura recursiva")
    parser.add_argument("--skip-if-pdfa", action="store_true", help="Pular arquivos já conformes PDF/A")
    parser.add_argument("--padroes", "-g", nargs="*", default=["*.pdf"], help="Padrões glob para seleção")

    args = parser.parse_args()
    res = asyncio.run(import_folder(args.path, recursive=args.recursivo, patterns=args.padroes, skip_if_pdfa=args.skip_if_pdfa))
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _cli()
