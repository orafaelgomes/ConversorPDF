import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_ghostscript() -> str | None:
    candidates = ("gswin64c.exe", "gswin32c.exe", "gs", "gswin64.exe", "gswin32.exe")

    for binary in candidates:
        path = shutil.which(binary)
        if path:
            return path

    here = Path(__file__).resolve().parent
    for binary in candidates:
        candidate = here / binary
        if candidate.exists():
            return str(candidate)

    for root in (Path(r"C:\Program Files\gs"), Path(r"C:\Program Files (x86)\gs")):
        if not root.exists():
            continue
        for version_dir in sorted(root.glob("gs*"), key=lambda item: item.name, reverse=True):
            for bin_dir in (version_dir / "bin", root / "bin"):
                for binary in candidates:
                    candidate = bin_dir / binary
                    if candidate.exists():
                        return str(candidate)

    return None


def install_ghostscript(installer_path: str | None = None) -> bool:
    project_dir = Path(__file__).resolve().parent
    installer_candidates = []

    if installer_path:
        installer_candidates.append(Path(installer_path))
    installer_candidates.extend([
        project_dir / "gs10071w64.exe",
        project_dir / "ghostscript" / "gs10071w64.exe",
    ])

    installer = next((candidate for candidate in installer_candidates if candidate.exists()), None)
    if not installer:
        return False

    try:
        subprocess.run([str(installer), "/S", "/NCRC"], check=True, capture_output=True, text=True)
        return True
    except Exception:
        return False


def ensure_ghostscript() -> str | None:
    found = find_ghostscript()
    if found:
        return found

    if install_ghostscript():
        return find_ghostscript()
    return None


def get_ghostscript_command() -> str | None:
    return ensure_ghostscript()


if __name__ == "__main__":
    print(get_ghostscript_command() or "NOT_FOUND")
