#!/usr/bin/env python3
"""Compatibility wrapper for scripts/assets/build_companion_skill_index.mjs."""
from __future__ import annotations

import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'assets' / 'build_companion_skill_index.mjs'
raise SystemExit(subprocess.call(["node", str(SCRIPT)]))
