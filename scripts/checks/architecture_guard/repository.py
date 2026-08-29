"""Repository paths and deterministic file discovery for architecture checks."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


FRONTEND_SRC = ROOT / "frontend" / "src"


BACKEND = ROOT / "backend"


TS_SUFFIXES = {".ts", ".tsx"}


PY_SUFFIXES = {".py"}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_files(root: Path, suffixes: set[str]) -> list[Path]:
    if not root.exists():
        return []
    out: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in suffixes:
            continue
        if any(
            part in {"node_modules", "dist", "build", "__pycache__", ".venv"} for part in path.parts
        ):
            continue
        out.append(path)
    return out
