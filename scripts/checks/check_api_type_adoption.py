#!/usr/bin/env python3
"""Fail CI when runtime API wrapper files hand-write response object types.

Generated OpenAPI schemas are the source of truth for response/request shapes.
Feature-level domain types can still refine generated schemas, but API wrapper
files should alias or compose ApiSchemas/ApiRequestBody instead of declaring new
object literal response/request contracts by memory.
"""
from __future__ import annotations

import re
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
    FRONTEND_SRC / "shared" / "wallet" / "api",
]

ENFORCED_API_FILES = {
    FRONTEND_SRC / "shared" / "auth" / "authApi.ts",
    FRONTEND_SRC / "shared" / "progress" / "homeSummaryApi.ts",
}

# Object-literal exported aliases inside API files are usually duplicated API
# contracts. Move rich domain shapes to feature types.ts, or compose generated
# schemas with Omit/Pick/intersections in the API wrapper.
EXPORTED_OBJECT_TYPE_RE = re.compile(r"^export\s+type\s+\w+\s*=\s*\{")

ALLOWLIST = {
    # The auth store is state, not an API wrapper contract.
    "frontend/src/shared/auth/useAuth.ts",
    "frontend/src/shared/auth/types.ts",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def iter_ts_files(root: Path):
    if not root.exists():
        return
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in {".ts", ".tsx"}:
            continue
        if path.name.endswith((".test.ts", ".test.tsx")):
            continue
        if any(part in {"node_modules", "dist", "build", "__pycache__"} for part in path.parts):
            continue
        yield path


def main() -> int:
    violations: list[str] = []
    paths: list[Path] = []
    for api_dir in ENFORCED_API_DIRS:
        paths.extend(list(iter_ts_files(api_dir) or []))
    paths.extend(path for path in ENFORCED_API_FILES if path.exists())

    for path in sorted(set(paths)):
        path_rel = rel(path)
        if path_rel in ALLOWLIST:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
            if EXPORTED_OBJECT_TYPE_RE.search(line.strip()):
                violations.append(f"{path_rel}:{lineno}: exported API object type should compose generated ApiSchemas/ApiRequestBody: {line.strip()}")
    if violations:
        print("Manual API type declarations found:", file=sys.stderr)
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        print(
            "\nUse ApiSchemas[...] / ApiRequestBody[...] aliases or move rich UI/domain-only types to feature types.ts.",
            file=sys.stderr,
        )
        return 1
    print("Runtime API wrapper types compose the generated API contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
