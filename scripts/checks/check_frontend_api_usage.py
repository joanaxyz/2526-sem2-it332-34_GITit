#!/usr/bin/env python3
"""Fail CI when runtime frontend API wrappers bypass the generated API contract.

Direct apiRequest calls are still allowed for low-schema admin/authoring tools and
inside the HTTP client itself. User-facing runtime modules must call
apiOperationRequest so methods and payload/response shapes stay tied to the
committed OpenAPI contract.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND_SRC = ROOT / "frontend" / "src"

ENFORCED_API_DIRS = [
    FRONTEND_SRC / "features" / "adventures" / "api",
    FRONTEND_SRC / "features" / "challenges" / "api",
    FRONTEND_SRC / "features" / "home" / "api",
    FRONTEND_SRC / "features" / "shop" / "api",
    FRONTEND_SRC / "features" / "skills" / "api",
    FRONTEND_SRC / "features" / "stats" / "api",
    FRONTEND_SRC / "features" / "track-map" / "api",
    FRONTEND_SRC / "shared" / "auth",
    FRONTEND_SRC / "shared" / "cosmetics",
    FRONTEND_SRC / "shared" / "progress",
    FRONTEND_SRC / "shared" / "wallet" / "api",
]

ALLOWLIST = {
    "frontend/src/shared/api/httpClient.ts",
    "frontend/src/shared/api/httpClient.test.ts",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_ts_files(root: Path):
    if not root.exists():
        return
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in {".ts", ".tsx"}:
            continue
        if any(part in {"node_modules", "dist", "build", "__pycache__"} for part in path.parts):
            continue
        yield path


def main() -> int:
    violations: list[str] = []
    for api_dir in ENFORCED_API_DIRS:
        for path in iter_ts_files(api_dir) or []:
            path_rel = rel(path)
            if path_rel in ALLOWLIST or path.name.endswith(".test.ts") or path.name.endswith(".test.tsx"):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for lineno, line in enumerate(text.splitlines(), start=1):
                if "apiRequest" in line and "apiOperationRequest" not in line:
                    violations.append(
                        f"{path_rel}:{lineno}: runtime API wrappers must use apiOperationRequest, not apiRequest: {line.strip()}"
                    )
    if violations:
        print("Frontend API contract usage violations found:", file=sys.stderr)
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        print(
            "\nUse apiOperationRequest(operationId, runtimePath, ...) so request methods and types come from the generated OpenAPI contract.",
            file=sys.stderr,
        )
        return 1
    print("Frontend runtime API wrappers use the generated API contract helper.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
