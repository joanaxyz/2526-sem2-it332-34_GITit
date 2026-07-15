#!/usr/bin/env python3
"""Compatibility wrapper for scripts/packaging/clean_repository_artifacts.py."""
from __future__ import annotations

import runpy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'packaging' / 'clean_repository_artifacts.py'
runpy.run_path(str(SCRIPT), run_name="__main__")
