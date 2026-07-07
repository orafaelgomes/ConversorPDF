"""
Logger simples que grava entradas em formato JSON Lines (JSONL).
Cada chamada a `log_event` adiciona uma linha JSON no arquivo `logs/import.log`.
"""
import json
from pathlib import Path
from datetime import datetime

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "import.log"


def log_event(event: dict):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        **event,
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry


def read_recent(path: str, n: int = 3):
    """Lê as últimas `n` entradas do log relacionadas a `path`.

    Retorna lista de dicionários (mais recentes primeiro).
    """
    if not LOG_FILE.exists():
        return []
    out = []
    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("path") == path:
                out.append(obj)
    return out[-n:][::-1]


def read_all(path: str):
    """Lê todas as entradas do log relacionadas a `path`.

    Retorna lista de dicionários na ordem cronológica.
    """
    if not LOG_FILE.exists():
        return []
    out = []
    with LOG_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("path") == path:
                out.append(obj)
    return out
