#!/usr/bin/env python3
"""Compatibility wrapper for scripts/packaging/package_source_zip.py."""
from __future__ import annotations

import runpy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'packaging' / 'package_source_zip.py'
runpy.run_path(str(SCRIPT), run_name="__main__")
