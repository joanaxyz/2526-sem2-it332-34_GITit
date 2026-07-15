#!/usr/bin/env python3
"""Replay authored curriculum solutions and fail if generated targets are stale.

This is the expensive Phase 6 guard. It requires both backend Python
requirements and frontend Node dependencies because the target generator replays
solutions through the real TypeScript git simulator.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
FRONTEND_NODE_MODULES = ROOT / "frontend" / "node_modules"


def main() -> int:
    if not FRONTEND_NODE_MODULES.exists():
        print(
            "frontend/node_modules is missing; run `cd frontend && npm ci` before "
            "checking generated curriculum targets.",
            file=sys.stderr,
        )
        return 1

    env = os.environ.copy()
    env.setdefault("DJANGO_DEBUG", "True")
    env.setdefault("DJANGO_SECRET_KEY", "generated-target-check")

    result = subprocess.run(
        [sys.executable, "manage.py", "generate_targets", "--check"],
        cwd=BACKEND,
        env=env,
        text=True,
    )
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
